// MIT License
// Copyright (c) 2026 OlcPanel Contributors

package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"sync"
	"time"

	"golang.org/x/time/rate"
)

var (
	statsFile    string
	rxBytes      int64
	txBytes      int64
	statsLock    sync.Mutex
	rxLimit      int64 // bytes per second, 0 = unlimited
	txLimit      int64 // bytes per second, 0 = unlimited
	rxLimiter    *rate.Limiter
	txLimiter    *rate.Limiter
)

func main() {
	port := flag.Int("port", 1080, "SOCKS5 port")
	stats := flag.String("stats", "/tmp/socks.stats", "Stats file path")
	rxLimitKB := flag.Int64("rx-limit", 0, "RX limit in KB/s (0 = unlimited)")
	txLimitKB := flag.Int64("tx-limit", 0, "TX limit in KB/s (0 = unlimited)")
	flag.Parse()

	statsFile = *stats
	rxLimit = *rxLimitKB * 1024
	txLimit = *txLimitKB * 1024

	// Initialize rate limiters
	if rxLimit > 0 {
		rxLimiter = rate.NewLimiter(rate.Limit(rxLimit), int(rxLimit))
	}
	if txLimit > 0 {
		txLimiter = rate.NewLimiter(rate.Limit(txLimit), int(txLimit))
	}

	// Start stats writer
	go writeStats()

	// Start SOCKS5 server
	listener, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", *port))
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	log.Printf("SOCKS5 proxy listening on port %d", *port)
	if rxLimit > 0 {
		log.Printf("RX limit: %d KB/s", *rxLimitKB)
	}
	if txLimit > 0 {
		log.Printf("TX limit: %d KB/s", *txLimitKB)
	}

	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}
		go handleConnection(conn)
	}
}

func writeStats() {
	for {
		time.Sleep(1 * time.Second)
		statsLock.Lock()
		data := fmt.Sprintf("%d %d\n", rxBytes, txBytes)
		statsLock.Unlock()
		os.WriteFile(statsFile, []byte(data), 0644)
	}
}

func handleConnection(client net.Conn) {
	defer client.Close()

	// SOCKS5 handshake
	buf := make([]byte, 256)
	n, err := client.Read(buf)
	if err != nil || n < 2 || buf[0] != 0x05 {
		return
	}

	// No authentication
	client.Write([]byte{0x05, 0x00})

	// Read request
	n, err = client.Read(buf)
	if err != nil || n < 7 || buf[0] != 0x05 || buf[1] != 0x01 {
		return
	}

	// Parse address
	var host string
	var port uint16

	switch buf[3] {
	case 0x01: // IPv4
		host = fmt.Sprintf("%d.%d.%d.%d", buf[4], buf[5], buf[6], buf[7])
		port = uint16(buf[8])<<8 | uint16(buf[9])
	case 0x03: // Domain
		length := int(buf[4])
		host = string(buf[5 : 5+length])
		port = uint16(buf[5+length])<<8 | uint16(buf[6+length])
	default:
		client.Write([]byte{0x05, 0x08, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}

	// Connect to target
	target, err := net.Dial("tcp", fmt.Sprintf("%s:%d", host, port))
	if err != nil {
		client.Write([]byte{0x05, 0x05, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}
	defer target.Close()

	// Success response
	client.Write([]byte{0x05, 0x00, 0x00, 0x01, 0, 0, 0, 0, 0, 0})

	// Relay traffic
	go relay(client, target, &txBytes, txLimiter)
	relay(target, client, &rxBytes, rxLimiter)
}

func relay(dst, src net.Conn, counter *int64, limiter *rate.Limiter) {
	buf := make([]byte, 32*1024)
	for {
		n, err := src.Read(buf)
		if err != nil {
			return
		}

		// Apply rate limiting
		if limiter != nil {
			limiter.WaitN(nil, n)
		}

		_, err = dst.Write(buf[:n])
		if err != nil {
			return
		}

		statsLock.Lock()
		*counter += int64(n)
		statsLock.Unlock()
	}
}
