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

impl ActiveSession {
    pub fn stop(self) -> Session {
        let end = SystemTime::now();

        let duration = end
            .duration_since(self.start)
            .unwrap_or(Duration::from_secs(0))
            .as_secs();

        Session {
            start: self.start,
            end,
            tags: self.tags,
            notes: self.notes,
        }
    }
}
