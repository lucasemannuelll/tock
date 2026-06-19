#![forbid(unsafe_code)]

use chrono::{DateTime, Local, TimeZone};
use std::collections::HashMap;

pub fn print_summary(lines: &[String]) {
    let today = Local::now().date_naive();

    let mut total_today = 0u64;

    let mut tags: HashMap<String, u64> = HashMap::new();

    let mut last_line: Option<&String> = None;

    for line in lines.iter().skip(1) {
        let parts: Vec<&str> = line.splitn(5, ',').collect();

        if parts.len() != 5 {
            continue;
        }

        let start: i64 = match parts[0].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        let duration: u64 = match parts[2].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        let dt: DateTime<Local> = match Local.timestamp_opt(start, 0).single() {
            Some(v) => v,
            None => continue,
        };

        if dt.date_naive() == today {
            total_today += duration;

            for tag in parts[3].split('|') {
                *tags.entry(tag.to_string()).or_insert(0) += duration;
            }
        }

        last_line = Some(line);
    }

    println!();
    println!("=== Resumo de Hoje ===");
    println!();

    println!(
        "Total registrado: {}h {}min",
        total_today / 3600,
        (total_today / 3600) / 60
    );

    let mut entries: Vec<_> = tags.into_iter().collect();

    entries.sort_by(|a, b| b.1.cmp(&a.1));

    for (tag, secs) in entries.iter().take(5) {}
}
