#![forbid(unsafe_code)]

use crate::session::Session;
use std::{
    env,
    fs::{File, OpenOptions},
    io::{BufRead, BufReader, Write},
    path::PathBuf,
    time::{SystemTime, UNIX_EPOCH},
};

pub fn csv_path() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let home = env::var("HOME")?;
    Ok(PathBuf::from(home).join("time-track.csv"))
}

pub fn ensure_csv_exists() -> Result<(), Box<dyn std::error::Error>> {
    let path = csv_path()?;

    if !path.exists() {
        let mut file = File::create(path)?;

        writeln!(file, "start,end,duration_secs,tags,notes")?;
    }

    Ok(())
}

fn unix_timestamp(time: SystemTime) -> Result<u64, Box<dyn std::error::Error>> {
    Ok(time.duration_since(UNIX_EPOCH)?.as_secs())
}

pub fn append_session(session: &Session) -> Result<(), Box<dyn std::error::Error>> {
    let path = csv_path()?;

    let mut file = OpenOptions::new().append(true).open(path)?;

    let tags = session.tags.replace(',', "|");
    let notes = session.notes.replace('\n', " ");

    writeln!(
        file,
        "{},{},{},{},{}",
        unix_timestamp(session.start)?,
        unix_timestamp(session.end)?,
        session.duration_secs,
        tags,
        notes
    )?;

    file.flush()?;

    Ok(())
}

pub fn read_lines() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let path = csv_path()?;

    let file = File::open(path)?;

    let reader = BufReader::new(file);

    let mut lines = Vec::new();

    for line in reader.lines() {
        lines.push(line?);
    }

    Ok(lines)
}
