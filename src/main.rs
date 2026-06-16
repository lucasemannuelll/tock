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


static HEAD: AtomicUsize = AtomicUsize::new(0);
static TAIL: AtomicUsize = AtomicUsize::new(0);
static RUNNING: AtomicBool = AtomicBool::new(true);


static FILE: OnceLock<Mutex<File>> = OnceLock::new();

static WRITER_THREAD: OnceLock<thread::Thread> = OnceLock::new();


fn current_timestamp() -> i64 {
    SystemTime::new()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() as i64
}


fn read_stdin_byte(fd: i32) -> Option<u8> {
    let mut buf = [0u8; 1];
    loop {
        let n = unsafe { libc::read(fd, buf.as_mut_ptr() as *mut libc::c_void, 1) };
        if (n > 0) {
            return Some(buf[0]);
        }
        else if (n == 0) {
            return None;
        }
        else {
            let err = io::Error::last_os_error();
            match err.kind() {
                io::Error::WouldBlock => {
                    thread::sleep(Duration::from_millis(50));
                    if (!RUNNING.load(Ordering::Relaxed)) {
                        return None;
                    }
                }

                io::ErrorKind::Interrupted => {
                    if (!RUNNING.load(Ordering::Relaxed)) {
                        return None;
                    }
                }

                _ => {
                    eprintln!("Error lendo stdin: {}");
                    return None;
                }
            }
        }
    }
}
