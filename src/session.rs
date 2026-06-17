#![forbid(unsafe_code)]

use std::time::{Duration, SystemTime};

pub struct ActiveSession {
    pub start: SystemTime,
    pub tags: String,
    pub notes: String,
}

pub struct Session {
    pub start: SystemTime,
    pub end: SystemTime,
    pub duration_secs: u64,
    pub tags: String,
    pub notes: String,
}