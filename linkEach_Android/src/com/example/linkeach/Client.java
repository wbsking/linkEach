package com.example.linkeach;

import java.io.*;
import java.net.*;

public class Client{
	
	public Socket sock;
	
	public Client(){
		sock = new Socket();
	}
	
	public void connect(String remote_ip) throws IOException{
		sock.connect(new InetSocketAddress(remote_ip, Consts.SERVER_PORT));
	}
	
	public void connect(String remote_ip, int port) throws IOException{
		sock.connect(new InetSocketAddress(remote_ip, port));
	}
	
	public void send_msg(String msg) throws IOException{
		BufferedWriter out = new BufferedWriter(new OutputStreamWriter(sock.getOutputStream()));
		out.write(msg);
		out.flush();
	}
	
	public String recv_msg() throws IOException{
		BufferedReader in = new BufferedReader(new InputStreamReader(sock.getInputStream()));
		return in.readLine();
	}
	
	public void colse() throws IOException{
		sock.close();
	}
}