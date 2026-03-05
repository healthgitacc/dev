#!/usr/bin/env node
/**
 * Frontend startup script
 * This script starts the Next.js development server
 */

const { spawn } = require('child_process');
const path = require('path');

// Configuration
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || 'localhost';

// Start Next.js 
console.log(`Starting Next.js development server on ${HOST}:${PORT}...`);

const nextPath = path.join(__dirname, 'node_modules', '.bin', 'next');
const args = ['dev', '-p', PORT.toString()];

const server = spawn('node', [path.join(__dirname, 'node_modules', 'next', 'dist', 'bin', 'next.js'), ...args], {
  stdio: 'inherit',
  cwd: __dirname,
  shell: true
});

server.on('error', (err) => {
  console.error('Failed to start frontend:', err);
  process.exit(1);
});

server.on('exit', (code) => {
  console.log(`Frontend server exited with code ${code}`);
  process.exit(code);
});
