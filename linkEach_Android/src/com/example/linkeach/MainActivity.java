package com.example.linkeach;

import java.io.IOException;
import java.util.*;
import java.util.Map.Entry;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.Context;
import android.graphics.Color;
import android.view.Gravity;
import android.view.Menu;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.view.View.OnClickListener;
import android.view.View.OnTouchListener;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.RelativeLayout.LayoutParams;
import android.widget.TextView;
import android.widget.ProgressBar;
import android.view.animation.TranslateAnimation;

public class MainActivity extends Activity{
	public List cast_label_list;
	public Map cast_map;
	public ProgressBar loading_bar;
	public chkHandler chk_handler;
	public connHandler conn_handler;
	public checkThd chk_thd;
	public TextView cast_label;
	public RelativeLayout main_layout;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		cast_label_list = new ArrayList<Map>();
		
		setContentView(R.layout.activity_main);
		chk_handler = new chkHandler();
		
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
		String name = tmp_map.get("name");
		cast_label = new TextView(this);
		cast_label.setBackgroundColor(Color.rgb(0, 178, 238));
		cast_label.setText(client_ip);
		cast_label.setTextSize(20);
		cast_label.setGravity(Gravity.CENTER);
		cast_label.setVisibility(View.VISIBLE);
		cast_label.setClickable(true);
		
		int label_id = cast_label.getId();
		Map tmp = new HashMap<Object, Object>();
		tmp.put("label", cast_label);
		tmp.put("name", name);
		tmp.put("show", false);
		tmp.put("ip", client_ip);
		tmp.put("label_id", label_id);
		
		cast_label.setOnTouchListener(new View.OnTouchListener() {
			
			@Override
			public boolean onTouch(View v, MotionEvent event) {
				MainActivity.this.cast_label_click(v, event);
				return false;
			}
		});
		
		int margin_top = 0;
		for(Iterator it=cast_label_list.iterator();it.hasNext();){
			Map cast_map = (Map)it.next();
			margin_top += 100;
			if((Boolean) cast_map.get("show")){
				margin_top += 80;
			}
		}
		main_layout = (RelativeLayout)findViewById(R.id.main_layout);
		LayoutParams rp = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT);
		rp.topMargin = margin_top;
		
		ValueAnimator tn = ObjectAnimator.ofInt(cast_label, "height", 0, 100);;
		tn.setDuration(500);
		tn.start();
		main_layout.addView(cast_label, rp);
		cast_label_list.add(tmp);
	}
	
	public void cast_label_click(View v, MotionEvent event){
		if(MotionEvent.ACTION_DOWN == event.getAction()){
			v.setBackgroundColor(Color.rgb(0, 153, 204));
		}
		else if(MotionEvent.ACTION_UP == event.getAction()){
			v.setBackgroundColor(Color.rgb(0, 178, 238));
			for(int i=0; i<cast_label_list.size();i++){
				Map tmp = (Map)cast_label_list.get(i);
				if((Integer)tmp.get("label_id") == v.getId()){
					if(!tmp.containsKey("client")){
						try{
							conn_handler = new connHandler((String)tmp.get("ip"));
							tmp.put("client", conn_handler);
							LinearLayout ctrl_layout = new LinearLayout(this);
							LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(180, 80);
							ctrl_layout.setGravity(Gravity.CENTER);
							ctrl_layout.setOrientation(0);
							ctrl_layout.setBackgroundColor(Color.rgb(0, 153, 204));
							Button power_btn = new Button(this);
							Button reboot_btn = new Button(this);
							
							power_btn.setOnClickListener(new OnClickListener(){
								public void onClick(View v){
									Message msg = new Message();
									Bundle bund = new Bundle();
									bund.putString("cmd", Consts.SHUTDOWN_MSG);
									msg.setData(bund);
									conn_handler.sendMessage(msg);
								}
							});
							
							reboot_btn.setOnClickListener(new OnClickListener(){
								public void onClick(View v){
									Message msg = new Message();
									Bundle bund = new Bundle();
									bund.putString("cmd", Consts.REBOOT_MSG);
									msg.setData(bund);
									conn_handler.sendMessage(msg);
								}
							});
							
							power_btn.setText("ShutDown");
							reboot_btn.setText("Reboot");
							
							ctrl_layout.addView(power_btn, lp);
							ctrl_layout.addView(reboot_btn, lp);
							
							main_layout = (RelativeLayout)findViewById(R.id.main_layout);
							RelativeLayout.LayoutParams rp = new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT);
							rp.topMargin = v.getTop() + 100;
							
							tmp.put("ctrl_label", ctrl_layout);
							tmp.put("show", true);
							main_layout.addView(ctrl_layout, rp);
							
						}
						catch(Exception ex){
							ex.printStackTrace();
						}
					
					}else if((Boolean)tmp.get("show")){
						LinearLayout ctrl_label = (LinearLayout)tmp.get("ctrl_label");
						LayoutParams rp = (LayoutParams) ctrl_label.getLayoutParams();
						rp.height = 0;
						ctrl_label.setLayoutParams(rp);
					}else{
						
					}
				}
			}
		}
	}
	
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
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
				for(Map.Entry<String, Map> entry:remote_clients.entrySet()){
					String client_ip = entry.getKey();
					int i;
					int cast_len = MainActivity.this.cast_label_list.size();
					for(i=0; i<cast_len; i++){
						Map element = (Map)MainActivity.this.cast_label_list.get(i);
						if(element.get("ip") == client_ip){
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
	
	class connHandler extends Handler{
		Client cli;
		String remote_ip;
		String msg;
		
		public connHandler(String ip){
			remote_ip = ip;
			cli = new Client();
		}
		
		public void handleMessage(Message msg){
			if(msg!=null){
				try{
					String cmd = (String) msg.getData().get("cmd");
					connThd conn = new connThd(cli, remote_ip, cmd);
					conn.start();
				}
				catch(Exception ex){
					ex.printStackTrace();
				}
			}
		}
	}
	
	class connThd extends Thread{
		public Client conn;
		String ip;
		String msg;
		
		public connThd(Client conn, String ip, String msg){
			this.conn =conn; 
			this.ip = ip;
			this.msg = msg;
		}
		
		public void run(){
			try{
				if(!this.conn.is_conn){
					this.conn.connect(ip);
				}
				this.conn.send_msg(this.msg);
				
			}catch(Exception ex){
				ex.printStackTrace();
			}
		}
		
	}
}




