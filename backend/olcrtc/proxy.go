package main

import (
	"encoding/json"
	"log"
	"net"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	socks5 "github.com/armon/go-socks5"
)

type AppConfig struct {
	ListenAddr    string
	StatsFile     string
	FlushInterval time.Duration
	LogPrefix     string
}

type StatsSnapshot struct {
	UploadBytes      uint64 `json:"upload_bytes"`
	DownloadBytes    uint64 `json:"download_bytes"`
	TotalBytes       uint64 `json:"total_bytes"`
	UploadRateBps    uint64 `json:"upload_rate_bps"`
	DownloadRateBps  uint64 `json:"download_rate_bps"`
	ConnectionsOpen  int64  `json:"connections_open"`
	ConnectionsTotal uint64 `json:"connections_total"`
	StartedAt        string `json:"started_at"`
	UpdatedAt        string `json:"updated_at"`
}

type StatsManager struct {
	uploadBytes      uint64
	downloadBytes    uint64
	connectionsOpen  int64
	connectionsTotal uint64

	startedAt time.Time

	mu         sync.Mutex
	lastTick   time.Time
	lastUpload uint64
	lastDown   uint64
}

func NewStatsManager() *StatsManager {
	now := time.Now().UTC()
	return &StatsManager{
		startedAt: now,
		lastTick:  now,
	}
}

func (s *StatsManager) IncOpen() {
	atomic.AddInt64(&s.connectionsOpen, 1)
	atomic.AddUint64(&s.connectionsTotal, 1)
}

func (s *StatsManager) DecOpen() {
	atomic.AddInt64(&s.connectionsOpen, -1)
}

func (s *StatsManager) AddUpload(n uint64) {
	if n > 0 {
		atomic.AddUint64(&s.uploadBytes, n)
	}
}

func (s *StatsManager) AddDownload(n uint64) {
	if n > 0 {
		atomic.AddUint64(&s.downloadBytes, n)
	}
}

func (s *StatsManager) Snapshot() StatsSnapshot {
	upload := atomic.LoadUint64(&s.uploadBytes)
	download := atomic.LoadUint64(&s.downloadBytes)

	return StatsSnapshot{
		UploadBytes:      upload,
		DownloadBytes:    download,
		TotalBytes:       upload + download,
		ConnectionsOpen:  atomic.LoadInt64(&s.connectionsOpen),
		ConnectionsTotal: atomic.LoadUint64(&s.connectionsTotal),
		StartedAt:        s.startedAt.Format(time.RFC3339Nano),
		UpdatedAt:        time.Now().UTC().Format(time.RFC3339Nano),
	}
}

func (s *StatsManager) Rates() (uploadRate uint64, downloadRate uint64) {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now().UTC()
	elapsed := now.Sub(s.lastTick).Seconds()
	if elapsed <= 0 {
		return 0, 0
	}

	upload := atomic.LoadUint64(&s.uploadBytes)
	down := atomic.LoadUint64(&s.downloadBytes)

	du := upload - s.lastUpload
	dd := down - s.lastDown

	s.lastUpload = upload
	s.lastDown = down
	s.lastTick = now

	uploadRate = uint64(float64(du) / elapsed)
	downloadRate = uint64(float64(dd) / elapsed)
	return uploadRate, downloadRate
}

func (s *StatsManager) SnapshotWithRates() StatsSnapshot {
	snap := s.Snapshot()
	up, down := s.Rates()
	snap.UploadRateBps = up
	snap.DownloadRateBps = down
	snap.UpdatedAt = time.Now().UTC().Format(time.RFC3339Nano)
	return snap
}

func writeStatsLoop(stats *StatsManager, path string, interval time.Duration, stop <-chan struct{}) {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		log.Printf("stats mkdir: %v", err)
		return
	}

	writeOnce := func() {
		snap := stats.SnapshotWithRates()

		tmp, err := os.CreateTemp(dir, ".stats-*.json")
		if err != nil {
			log.Printf("stats create temp: %v", err)
			return
		}

		enc := json.NewEncoder(tmp)
		enc.SetIndent("", "  ")
		if err := enc.Encode(snap); err != nil {
			_ = tmp.Close()
			_ = os.Remove(tmp.Name())
			log.Printf("stats encode: %v", err)
			return
		}

		if err := tmp.Close(); err != nil {
			_ = os.Remove(tmp.Name())
			log.Printf("stats close: %v", err)
			return
		}

		if err := os.Rename(tmp.Name(), path); err != nil {
			_ = os.Remove(tmp.Name())
			log.Printf("stats rename: %v", err)
			return
		}
	}

	writeOnce()

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			writeOnce()
		case <-stop:
			writeOnce()
			return
		}
	}
}

type countingConn struct {
	net.Conn
	stats  *StatsManager
	closed sync.Once
}

func (c *countingConn) Read(p []byte) (int, error) {
	n, err := c.Conn.Read(p)
	if n > 0 {
		c.stats.AddUpload(uint64(n))
	}
	return n, err
}

func (c *countingConn) Write(p []byte) (int, error) {
	n, err := c.Conn.Write(p)
	if n > 0 {
		c.stats.AddDownload(uint64(n))
	}
	return n, err
}

func (c *countingConn) Close() error {
	var err error
	c.closed.Do(func() {
		c.stats.DecOpen()
		err = c.Conn.Close()
	})
	return err
}

type countingListener struct {
	net.Listener
	stats *StatsManager
}

func (l *countingListener) Accept() (net.Conn, error) {
	conn, err := l.Listener.Accept()
	if err != nil {
		return nil, err
	}

	l.stats.IncOpen()
	return &countingConn{
		Conn:  conn,
		stats: l.stats,
	}, nil
}

func loadConfig() AppConfig {
	return AppConfig{
		ListenAddr:    getenvDefault("LISTEN_ADDR", "127.0.0.1:1080"),
		StatsFile:     getenvDefault("STATS_FILE", "/var/lib/olcwave/stats.json"),
		FlushInterval: getenvDurationDefault("FLUSH_INTERVAL", time.Second),
		LogPrefix:     getenvDefault("LOG_PREFIX", "proxy"),
	}
}

func getenvDefault(key, def string) string {
	v := strings.TrimSpace(os.Getenv(key))
	if v == "" {
		return def
	}
	return v
}

func getenvDurationDefault(key string, def time.Duration) time.Duration {
	v := strings.TrimSpace(os.Getenv(key))
	if v == "" {
		return def
	}
	d, err := time.ParseDuration(v)
	if err != nil {
		return def
	}
	return d
}

func main() {
	cfg := loadConfig()
	stats := NewStatsManager()

	log.SetPrefix(cfg.LogPrefix + ": ")
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)

	ln, err := net.Listen("tcp", cfg.ListenAddr)
	if err != nil {
		log.Fatalf("listen %s: %v", cfg.ListenAddr, err)
	}
	defer ln.Close()

	stopStats := make(chan struct{})
	defer close(stopStats)

	go writeStatsLoop(stats, cfg.StatsFile, cfg.FlushInterval, stopStats)

	server, err := socks5.New(&socks5.Config{
		Rules:  socks5.PermitAll(),
		Logger: log.New(os.Stdout, "", log.LstdFlags|log.Lmicroseconds),
	})
	if err != nil {
		log.Fatalf("socks5 init: %v", err)
	}

	log.Printf("starting socks proxy listen=%s stats=%s", cfg.ListenAddr, cfg.StatsFile)

	if err := server.Serve(&countingListener{
		Listener: ln,
		stats:    stats,
	}); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
