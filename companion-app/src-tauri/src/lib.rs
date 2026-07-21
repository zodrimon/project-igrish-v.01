// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    Manager
};
use std::process::Command;
use std::process::Child;

struct BackendProcess {
    child: Option<Child>,
}

impl Drop for BackendProcess {
    fn drop(&mut self) {
        if let Some(mut child) = self.child.take() {
            println!("Killing backend process...");
            let _ = child.kill();
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let mut service_path = app.path().resource_dir().unwrap();
            
            let mut possible_path_1 = service_path.clone();
            possible_path_1.push("backend");
            possible_path_1.push("melissa-service.exe");
            
            let mut possible_path_2 = service_path.clone();
            possible_path_2.push("melissa-service.exe");

            let target_path = if possible_path_1.exists() {
                possible_path_1
            } else if possible_path_2.exists() {
                possible_path_2
            } else {
                possible_path_2 // Default to fallback for logging
            };
            
            println!("Starting backend service at {:?}", target_path);
            
            if target_path.exists() {
                let data_dir = app.path().app_local_data_dir().unwrap();
                std::fs::create_dir_all(&data_dir).unwrap_or_else(|e| eprintln!("Failed to create data dir: {}", e));
                
                // In production, start the service
                match Command::new(&target_path).current_dir(&data_dir).spawn() {
                    Ok(child) => {
                        println!("Started backend service with PID: {}", child.id());
                        app.manage(BackendProcess { child: Some(child) });
                    }
                    Err(e) => {
                        eprintln!("Failed to start backend service: {}", e);
                    }
                }
            } else {
                println!("Backend service not found at {:?}, assuming dev mode.", target_path);
            }
            
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>).unwrap();
            let restart_i = MenuItem::with_id(app, "restart", "Restart Backend", true, None::<&str>).unwrap();
            let settings_i = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>).unwrap();
            
            let menu = Menu::with_items(app, &[&settings_i, &restart_i, &quit_i]).unwrap();
            
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .menu_on_left_click(true)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        app.exit(0);
                    }
                    "restart" => {
                        println!("Restart backend requested.");
                        // Handle restart logic later
                    }
                    "settings" => {
                        println!("Settings requested.");
                        // Open settings window logic later
                    }
                    _ => {}
                })
                .build(app).unwrap();
                
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
