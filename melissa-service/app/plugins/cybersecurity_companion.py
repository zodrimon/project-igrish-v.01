from typing import Dict, Any, Optional
from app.plugins.base import PluginBase
from app.core.context_snapshot import global_context_snapshot

class CybersecurityCompanionPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "CybersecurityCompanion"
        
    async def get_context_facts(self) -> Dict[str, Any]:
        """
        Check the active window and process list to detect cybersecurity tools,
        labs (HTB, THM, CTF), or related activities.
        """
        facts = {}
        snapshot = global_context_snapshot.get_state()
        
        # 1. Check active window for lab platforms or tools
        active_window_data = snapshot.get("active_window", {})
        title = active_window_data.get("title", "").lower()
        
        if title:
            # Platform detection
            if "hack the box" in title or "htb" in title:
                facts["cyber_lab_platform"] = "Hack The Box"
            elif "tryhackme" in title or "thm" in title:
                facts["cyber_lab_platform"] = "TryHackMe"
            elif "ctf" in title:
                facts["cyber_lab_platform"] = "CTF"
                
            # Tool detection in window title (e.g. Burp Suite, Wireshark, Ghidra)
            if "burp suite" in title:
                facts["active_cyber_tool"] = "Burp Suite"
            elif "wireshark" in title:
                facts["active_cyber_tool"] = "Wireshark"
            elif "ghidra" in title:
                facts["active_cyber_tool"] = "Ghidra"
            elif "x64dbg" in title:
                facts["active_cyber_tool"] = "x64dbg"
            elif "ida" in title and "pro" in title:
                facts["active_cyber_tool"] = "IDA Pro"

        # 2. Check process list for running tools (like openvpn, nmap)
        process_list_data = snapshot.get("process_list", {})
        processes = process_list_data.get("processes", [])
        
        running_tools = []
        for p in processes:
            p_name = p.lower()
            if "openvpn" in p_name:
                running_tools.append("OpenVPN")
            elif "nmap" in p_name:
                running_tools.append("Nmap")
            elif "metasploit" in p_name or "msfconsole" in p_name:
                running_tools.append("Metasploit")
            elif "sqlmap" in p_name:
                running_tools.append("SQLMap")
                
        # Deduplicate
        running_tools = list(set(running_tools))
        
        if running_tools:
            facts["background_cyber_tools"] = running_tools
            
        # Add a general flag if any cyber activity is detected
        if facts:
            facts["cybersecurity_activity_detected"] = True
            
        return facts
