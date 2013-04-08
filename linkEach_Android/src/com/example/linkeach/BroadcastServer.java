package com.example.linkeach;

import java.io.IOException;
import java.net.*;
import java.util.HashMap;
import java.util.Map;

class getClientsThd extends Thread{
	public DatagramSocket sock;
	public Map<String, Map> cast_clients;
	public boolean stop_flag = false;
	
	public getClientsThd(){
		try{
		sock = new DatagramSocket(Consts.BROADCAST_PORT);
		sock.setSoTimeout(5000);
		cast_clients = new HashMap<String, Map>();
		}
		catch(Exception e){
			System.out.println(e);
		}
	}
	public Map get_clients(){
		return cast_clients;
	}
	
	public void run(){
		while(!stop_flag){
			try{
				InetAddress addr;
				String ip_addr;
				
				byte[] data = new byte[Consts.MAX_RECVSIZE];
				DatagramPacket packet = new DatagramPacket(data, data.length);
				sock.receive(packet);
				addr = packet.getAddress();
				ip_addr = addr.getHostAddress();
				String name = new String(data, 2, packet.getLength());
				if(!cast_clients.containsKey(ip_addr)){
					Map tmp_map = new HashMap();
					tmp_map.put("count", -1);
					tmp_map.put("name", name);
					cast_clients.put(ip_addr, tmp_map);
				}	
				else{
					Map tmp_map = (HashMap)cast_clients.get(ip_addr);
					tmp_map.put("count", -1);
				}
			}
			catch(Exception e){
				System.out.println(e);
			}
			finally{
				for(Map.Entry<String, Map> entry:cast_clients.entrySet()){
					String client_ip = entry.getKey();
					Map<String, Integer> tmp_map = entry.getValue();
					int count = tmp_map.get("count");
					count += 1;
					if(count == 4){
						cast_clients.remove(client_ip);
					}
					tmp_map.put("count", count);
				}
			}
		}
	}
	
}

public class BroadcastServer{
	public boolean stop_flag = true;
	public Socket sock;
	public Map broad_clients;
	public getClientsThd get_client_thd;
	
	public void run(){
		get_client_thd = new getClientsThd();
		get_client_thd.start();
	}
	
	public Map get_clients(){
		return get_client_thd.get_clients();
	}
	
//	public static void main(String args[]){
//		getClientsThd get_client_thd = new getClientsThd();
//		get_client_thd.run();
//	}
	
}
