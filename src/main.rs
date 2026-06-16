use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::os::unix::io::AsRawFd;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Mutex, OnceLock};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use chrono::Local;
use dirs;


const TAG_LEN: usize = 64;
const NOTE_LEN: usize = 128;
const RING_BUFFER: usize = 512;


#[derive(Copy, Clone, Default)]
struct Event {
    start: i64,
    end: i64,
    tags: [u8; TAG_LEN],
    notes: [u8; NOTE_LEN],
}

static mut RING: [Event; RING_BUFFER] = [Event {
    start: 0,
    end: 0,
    tags: [0; TAG_LEN],
    notes: [0; NOTE_LEN],
}; RING_BUFFER];

