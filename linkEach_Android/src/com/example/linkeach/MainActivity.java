package com.example.linkeach;

import java.util.*;
import java.util.Map.Entry;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.app.Activity;
import android.content.Context;
import android.view.Menu;
import android.view.View;
import android.widget.TextView;
import android.widget.ProgressBar;

public class MainActivity extends Activity {
	public List cast_label_list;
	public Map cast_map;
	public ProgressBar loading_bar;
	public chkHandler chk_handler;
	public checkThd chk_thd;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		cast_label_list = new ArrayList<Map>();
		chk_handler = new chkHandler();
		
		setContentView(R.layout.activity_main);
		loading_bar = (ProgressBar)findViewById(R.id.loading_bar);
		this.show_loading();
		chk_thd = new checkThd();
		chk_thd.start();

	}

	public void show_loading(){
		loading_bar.setVisibility(View.VISIBLE);
	}
	
	public void hide_loading(){
		loading_bar.setVisibility(View.GONE);
	}
	
	public void add_cast_label(Entry<String, Map> entry){
		String client_ip = entry.getKey();
		Map<String, String> tmp_map = entry.getValue();
		
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}

	
	class castLabel extends TextView{

		public castLabel(Context context) {
			super(context);
		}
	}
	
	
	class checkThd extends Thread{
		private BroadcastServer br_server;
		public Map clients;
		public boolean stop_flag;
		
		public checkThd(){
			stop_flag = false;
			br_server = new BroadcastServer();
			br_server.run();
		}
		
		public void run(){
			while(!stop_flag){
				try{
					clients = br_server.get_clients();
					if(!clients.isEmpty()){
						Message msg = new Message();
						Bundle bund = new Bundle();
						bund.putSerializable("map", (HashMap)clients);
						msg.setData(bund);
						MainActivity.this.chk_handler.sendMessage(msg);
					}
					Thread.sleep(5000);
				}
				catch(Exception ex){
					System.out.println(ex);
				}
			}
		}
	}

	class chkHandler extends Handler{
		
		public chkHandler(){
			
		}
		
		public void handleMessage(Message msg){
			if(msg!=null){
				MainActivity.this.hide_loading();
				Map<String, Map> remote_clients = (Map)msg.getData().getSerializable("map");
				System.out.println(remote_clients);
				for(Map.Entry<String, Map> entry:remote_clients.entrySet()){
					String client_ip = entry.getKey();
					int i;
					int cast_len = MainActivity.this.cast_label_list.size();
					for(i=0; i<cast_len; i++){
						Map element = (Map)MainActivity.this.cast_label_list.get(i);
						if(element.containsKey(client_ip)){
							break;
						}
					}
					if(i==cast_len){
						MainActivity.this.add_cast_label(entry);
					}
				}
			}
		}
		
	}
}