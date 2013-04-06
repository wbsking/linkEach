package com.example.linkeach;

import java.io.*;
import java.net.*;

public class Client{
	
	public Socket sock;
	
	public Client(){
		sock = new Socket();
	}
	
	public void connect(String remote_ip){
	}
	
	public void connect(String remote_ip, int port){
		
	}
	
	public void send_msg(String msg){}
	
	public void recv_msg(){}
	
	public void colse() throws IOException{
		sock.close();
	}
}