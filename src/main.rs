mod session;
mod storage;
mod summary;

use session::ActiveSession;

use std::{
    error::Error,
    io::{self, Write},
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
    },
    time::SystemTime,
};

fn parse_start(line: &str) -> Option<(String, String)> {
    let rest = line.strip_prefix("start ")?;

    let mut parts = rest.splitn(2, ' ');

    let tags = parts.next()?.trim();

    let notes = parts.next()?.trim();

    if tags.is_empty() || notes.is_empty() {
        return None;
    }

    Some((tags.to_string(), notes.to_string()))
}

fn main() -> Result<(), Box<dyn Error>> {
    storage::ensure_csv_exists()?;

    let running = Arc::new(AtomicBool::new(true));

    {
        let running = Arc::clone(&running);

        ctrlc::set_handler(move || {
            running.store(false, Ordering::SeqCst);
        })?;
    }

    let mut active: Option<ActiveSession> = None;

    while running.load(Ordering::SeqCst) {
        print!("> ");
        io::stdout().flush()?;

        let mut line = String::new();

        let bytes = io::stdin().read_line(&mut line)?;

        if bytes == 0 {
            break;
        }

        let line = line.trim();

        if line.is_empty() {
            continue;
        }

        if line == "stop" {
            match active.take() {
                Some(session) => {
                    let finished = session.stop();

                    storage::append_session(&finished)?;

                    println!("Sessão finalizada");
                }

                None => {
                    println!("Nenhuma sessão em andamento");
                }
            }
            continue;
        }

        if line.starts_with("start ") {
            if active.is_some() {
                println!("Sessão já em andamento");

                println!("Use stop antes de iniciar outra");

                continue;
            }
            match parse_start(line) {
                Some((tags, notes)) => {
                    active = Some(ActiveSession {
                        start: SystemTime::now(),
                        tags,
                        notes,
                    });
                    println!("Sessão iniciada");
                }

                None => {
                    println!("Uso: start <tags> <nota>");
                }
            }

            continue;
        }
        println!("Comando desconhecido");
    }

    println!();
    println!("Encerrando...");

    let lines = storage::read_lines()?;

    summary::print_summary(&lines);

    Ok(())
}
