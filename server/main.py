# -*- coding: utf-8 -*-
import json,sys,time,random,math
sys.path.append('\\'.join(sys.path[0].split('\\')[:-2])+'\\functionsEx')
from threading import Thread
from functionsex import *
from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection

watchers=set()
rules=magicDict({'width':500,'height':500,'speed':35})
players=magicDict({'limit':2,'count':0,'minimum':2})
player={}

def gameCicle():
   while(players.count==players.minimum):
      points=[]
      objs=[]
      plrs=[]
      for plr in player:
         a=math.radians(player[plr]['direction'])
         b=(rules.speed/1000.0)*(getms()-player[plr]['lineTime'])
         nX=player[plr]['left']+math.sin(a)*b
         nY=player[plr]['top']+math.cos(a)*b
         points+=player[plr]['points']
         points.append([player[plr]['left'],player[plr]['top']])
         points.append([nX,nY])
         points.append(None)
         objs.append([[player[plr]['left'],player[plr]['top']],[nX,nY]])
         plrs.append([plr,False])
      j1=0
      for i in xrange(1,len(points)):
         if(points[i]==None): j1+=1
         if(points[i]==None or points[i-1]==None): continue
         for j2 in xrange(len(objs)):
            A=points[i]
            B=points[i-1]
            C=objs[j2][0]
            D=objs[j2][1]
            if(j2==j1 or A==B or C==D): continue
            s=intersectCheck(A,B,C,D)
            if(s[0] and s[1]>s[2]): plrs[j2][1]=s
      for plr in plrs:
         if(not(plr[1])): continue
         players.count-=1
         for a in watchers: a.send(json.dumps({'type':'playerDie','data':plr[0]}))
      if(players.count<players.minimum):
         for a in watchers: a.send(json.dumps({'type':'gameSet','data':False}))
         print 'Game over'
      time.sleep(0.05)

class playConn(SockJSConnection):
   pid=''
   def on_open(self,info):
      watchers.add(self)
      self.send(json.dumps({'type':'ruleSet','data':rules}))
      if(players.count<players.limit):
         players.count+=1
         id='player'+str(players.count)
         clr=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
         color='#'+random.choice(clr)+random.choice(clr)+random.choice(clr)
         left=50*players.count
         top=50*players.count
         direct=90
         player[id]={'id':id,'direction':direct,'color':color,'left':left,'top':top,'points':[],'lineTime':0}
         print 'Connected',id
         self.send(json.dumps({'type':'idSet','data':id}))
         self.send(json.dumps({'type':'timeSync','data':getms()}))
         if(players.count==players.minimum):
            for plr in player:
               player[plr]['lineTime']=getms()
               self.broadcast(watchers,json.dumps({'type':'playerSet','data':player[plr]}))
            Thread(None,gameCicle).start()
            self.broadcast(watchers,json.dumps({'type':'gameSet','data':True}))
            print 'Game begin!'
         else:
            self.broadcast(watchers,json.dumps({'type':'playerSet','data':player[id]}))
      else:
         id='watcher'
         print 'Connected',id
         self.send(json.dumps({'type':'idSet','data':id}))
         self.send(json.dumps({'type':'timeSync','data':getms()}))
         for plr in player: self.send(json.dumps({'type':'playerSet','data':player[plr]}))
         if(players.count==players.minimum): self.send(json.dumps({'type':'gameSet','data':True}))
      self.pid=id

   def on_message(self, msg):
      print 'recivedData',self.pid,msg
      msg=json.loads(msg)
      if(msg['type']=='kbEvent'):
         a=math.radians(player[self.pid]['direction'])
         b=(rules.speed/1000.0)*(msg['timestamp']-player[self.pid]['lineTime'])
         nX=player[self.pid]['left']+math.sin(a)*b
         nY=player[self.pid]['top']+math.cos(a)*b
         player[self.pid]['points'].append([player[self.pid]['left'],player[self.pid]['top']])
         player[self.pid]['left']=nX
         player[self.pid]['top']=nY
         player[self.pid]['lineTime']=msg['timestamp']
         dr={360:{'A':-1,'W':0,'S':0,'D':1},180:{'A':1,'W':0,'S':0,'D':-1},270:{'A':0,'W':-1,'S':1,'D':0},90:{'A':0,'W':1,'S':-1,'D':0}}
         a=player[self.pid]['direction']
         player[self.pid]['direction']=reAngle(a+90*dr[a][msg['data']])
         self.broadcast(watchers,json.dumps({'type':'playerSet','data':player[self.pid]}))

   def on_close(self):
      print self.pid
      watchers.remove(self)

playRtr=SockJSRouter(playConn,'/play',user_settings=dict(disabled_transports=[]))
app=web.Application(playRtr.urls)
app.listen(8081)
print 'Listen on 0.0.0.0:8081'
ioloop.IOLoop.instance().start()