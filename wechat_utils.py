# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 12:44:30 2017

@author: Quantum Liu
"""
import numpy as np
import scipy.io as sio
import itchat
from keras.callbacks import Callback
import time
import matplotlib.pyplot as plt
import matplotlib  
from math import ceil
from itchat.content import TEXT
import _thread
import os
from os import system
import re
import traceback  
matplotlib.use('Agg') # 
#==============================================================================
# def login():
#     itchat.auto_login(enableCmdQR=True)
#     itchat.run()
#     itchat.dump_login_status()
#     
#==============================================================================
#==============================================================================
# Automaticly login when imported 
#在被import时自动登录
#==============================================================================
itchat.auto_login(enableCmdQR=0.5,hotReload=True)
itchat.dump_login_status()#dump
#==============================================================================
# 
#==============================================================================
def send(text):
    #send text msgs to 'filehelper'
    #给文件助手发送文本信息
    itchat.send(text, toUserName='filehelper')
#==============================================================================
#     
#==============================================================================
class sendmessage(Callback):
    #A subclss of keras.callbacks.Callback class
    #keras.callbacks.Callback class的子类
    def shutdown(self,sec,save=True,filepath='temp.h5'):
        #Function used to shut down the computer
        #sec:waitting time to shut down the computer,sencond
        #save:wether saving the model
        #filepath:the filepath for saving the model
        #关机函数
        #sec:关机等待秒数
        #save:是否保存模型
        #filepath:保存模型的文件名
        if save:
            self.model.save(filepath, overwrite=True)
            itchat.send('Command accepted,the model has already been saved,shutting down the computer....', toUserName='filehelper')
        else:
            itchat.send('Command accepted,shutting down the computer....', toUserName='filehelper')
        _thread.start_new_thread(system, ('shutdown -s -t %d' %sec,))
#==============================================================================
#         
#==============================================================================
    def cancel(self):
        #Cancel function to cancel shutting down the computer
        #取消关机函数
        itchat.send('Command accepted,cancel shutting down the computer....', toUserName='filehelper')
        _thread.start_new_thread(system, ('shutdown -a',))
#==============================================================================
#         
#==============================================================================
    def GetMiddleStr(self,content,startStr,endStr):
        #get the string between two specified strings
        #从指定的字符串之间截取字符串
        try:
          startIndex = content.index(startStr)
          if startIndex>=0:
            startIndex += len(startStr)
          endIndex = content.index(endStr)
          return content[startIndex:endIndex]
        except:
            return ''
#==============================================================================
# 
#==============================================================================
    def validateTitle(self,title):
        #transform a string to a validate filename
        #将字符串转化为合法文件名
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
        new_title = re.sub(rstr, "", title)
        return new_title
#==============================================================================
#         
#==============================================================================
    def get_fig(self,level='all',metrics=['all']):
        #Get figure of train infomation
        #level:show the information of which level
        #metrics:metrics want to show,only show available ones
        #获取训练状态图表
        #level:显示batch级别函数epoch级别
        #metrics:希望获得的指标，只显示存在的指标，若指定了不存在的指标将不会被显示
        color_list='rgbyck'*10
        def batches(color_list='rgbyck'*10,metrics=['all']):
            if 'all' in metrics:
                m_available=list(self.logs_batches.keys())
            else:
                m_available=([val for val in list(self.logs_batches.keys()) if val in metrics]if[val for val in list(self.logs_batches.keys()) if val in metrics]else list(self.logs_batches.keys()))
            nb_rows_batches=int(ceil(len(m_available)/2))
            fig_batches=plt.figure('all_subs_batches')
            for i,k in enumerate(m_available):
                p=plt.subplot(nb_rows_batches,2,i+1)
                data=self.logs_batches[k]
                p.plot(range(len(data)),data,color_list[i]+'-',label=k)
                p.set_title(k+' in batches',fontsize=14)
                p.set_xlabel('batch',fontsize=10)
                p.set_ylabel(k,fontsize=10)
                p.legend()
            filename=self.validateTitle(self.localtime)+'batches.jpg'
            plt.savefig(filename)
            plt.close('all')
            itchat.send_image(filename,toUserName='filehelper')
            time.sleep(.5)
            itchat.send('Sending batches figure',toUserName='filehelper')
#==============================================================================
#             
#==============================================================================
        def epochs(color_list='rgbyck'*10,metrics=['all']):
            if 'all' in metrics:
                m_available=list(self.logs_epochs.keys())
            else:
                m_available=([val for val in list(self.logs_epochs.keys()) if val in metrics]if[val for val in list(self.logs_epochs.keys()) if val in metrics]else list(self.logs_epochs.keys()))
            nb_rows_epochs=int(ceil(len(m_available)/2))
            fig_epochs=plt.figure('all_subs_epochs')
            for i,k in enumerate(m_available):
                p=plt.subplot(nb_rows_epochs,2,i+1)
                data=self.logs_epochs[k]
                p.plot(range(len(data)),data,color_list[i]+'-',label=k)
                p.set_title(k+' in epochs',fontsize=14)
                p.set_xlabel('epoch',fontsize=10)
                p.set_ylabel(k,fontsize=10)
                p.legend()
            filename=self.validateTitle(self.localtime)+'epochs.jpg'
            plt.savefig(filename)
            plt.close('all')
            itchat.send_image(filename,toUserName='filehelper')
            time.sleep(.5)
            itchat.send('Sending epochs figure',toUserName='filehelper')
#==============================================================================
#             
#==============================================================================
        try:
            if not self.epoch and (level in ['all','epochs']):
                level='batches'
            if level=='all':
                batches(metrics=metrics)
                epochs(metrics=metrics)
                _thread.exit()
                return
            elif level=='epochs':
                epochs(metrics=metrics)
                _thread.exit()
                return
            elif level=='batches':
                batches(metrics=metrics)
                _thread.exit()
                return
            else:
                batches(metrics=metrics)
                epochs(metrics=metrics)
                _thread.exit()
                return
        except Exception:
            traceback.print_exc()
            itchat.send('Failed to send figure',toUserName='filehelper')
            _thread.exit()
            return
#==============================================================================
#             
#==============================================================================
    def gpu_status(self,av_type_list):
        for t in av_type_list:
            cmd='nvidia-smi -q --display='+t
            print('\nCMD:',cmd,'\n')
            r=os.popen(cmd)
            info=r.readlines()
            r.close()
            content = " ".join(info)
            print('\ncontent:',content,'\n')
            index=content.find('Attached GPUs')
            s=content[index:].replace(' ','').rstrip('\n')
            itchat.send(s, toUserName='filehelper')
            time.sleep(.5)
        #_thread.exit()
#==============================================================================
# 
#==============================================================================
    def on_train_begin(self, logs={}):
        self.epoch=[]
        self.logs_batches={}
        self.logs_epochs={}
        self.localtime = time.asctime( time.localtime(time.time()) )
        self.mesg = 'Train started at: '+self.localtime
        itchat.send(self.mesg, toUserName='filehelper')
        self.stopped_epoch = self.params['nb_epoch']
        @itchat.msg_register(TEXT)
#==============================================================================
#         registe methods to reply msgs,similar to main()
#         注册消息响应方法，相当于主函数
#==============================================================================
        def manualstop(msg):
            text=msg['Text']
            stop_training_cmdlist=['Stop now',"That's enough",u'停止训练',u'放弃治疗']
            #The keywords of stop training,if any of them is in the msg you sent,the command would be accepted
            #停止训练的关键词列表，发送的消息中包含任意一项都可触发命令
            shut_down_cmdlist=[u'关机','Shut down','Shut down the computer',u'别浪费电了',u'洗洗睡吧']
            #The keywords of shutting down,similair to stop_training_cmdlist
            #关机关键词列表，和stop_training_cmdlist类似
            cancel_cmdlist=[u'取消','cancel','aaaa']
            #The keywords of cancel shutting down,similair to stop_training_cmdlist
            #取消关机关键词列表，和stop_training_cmdlist类似
            get_fig_cmdlist=[u'获取图表','Show me the figure']
            #The keywords of getting figure,similair to stop_training_cmdlist
            #获取图表关键词列表，和stop_training_cmdlist类似
            gpu_cmdlist=['GPU','gpu',u'显卡']
            type_list=['MEMORY', 'UTILIZATION', 'ECC', 'TEMPERATURE', 'POWER', 'CLOCK', 'COMPUTE', 'PIDS', 'PERFORMANCE', 'SUPPORTED_CLOCKS,PAGE_RETIREMENT', 'ACCOUNTING']
            print('\n',text,'\n')
            if msg['ToUserName']=='filehelper':
                if 'Stop at' in text:
                    # Specify stop epoch，training will be stop after that epoch
                    #指定停止轮数，训练在指定epoch完成后会停止
                    #Example:send:'Stop at:8' from your phone,and then training will be stopped after epoch8
                    #例如：手机发送“Stop at：8”，训练将在epoch8完成后停止
                    self.stopped_epoch = int(re.findall(r"\d+\.?\d*",text)[0])
                    itchat.send('Command accepted,training will be stopped at epoch'+str(self.stopped_epoch), toUserName='filehelper')
#==============================================================================
#                 
#==============================================================================
                if any((k in text) for k in stop_training_cmdlist) :
                    #Stop training after current epoch finished
                    #当前epoch完成后停止训练
                    #example：send:'Stop now' or send:'停止训练' from your phone,and then training will be stopped after current epoch
                    #例如：手机发送“停止训练”或者“Stop now”，训练将会在当前epoch完成后被停止
                    self.model.stop_training = True
                    itchat.send('Command accepted,stop training now at epoch'+str(self.epoch[-1]+1), toUserName='filehelper')
#==============================================================================
#                 
#==============================================================================
                if any((k in text) for k in shut_down_cmdlist):
                    #Shutting down the computer after specified sec，specify waiting seconds and saved model filename by {sec} and [name](without .h5)
                    #在指定秒数后关机，用{sec}和[name]指定等待时间和保存文件名,文件名不包括.h5
                    #example:send:'Shut down now [test]{120}' from phone,the computer will be shut down after 120s,and save the model as test.h5
                    #or send:'Shut down now{120},don't save',then the model won't be saved.
                    if any((k in text) for k in [u'不保存模型',"don't save"]):
                        save=False
                    else:
                        save=True
                        filepath=(self.GetMiddleStr(text,'[',']')+'.h5' if self.GetMiddleStr(text,'[',']') else self.validateTitle(self.localtime)+'.h5')
                    sec=(int(self.GetMiddleStr(text,'{','}')) if int(self.GetMiddleStr(text,'{','}'))>30 else 120)
                    self.shutdown(sec,save=save,filepath=filepath)
#==============================================================================
#                     
#==============================================================================
                if any((k in text) for k in cancel_cmdlist):
                    #Cancel shutting down the computer
                    self.cancel()
#==============================================================================
#                     
#==============================================================================
                if any((k in text) for k in get_fig_cmdlist):   
                    #Get figure of train infomation,specify metrics and level you want to show by[metrics]and{level},defualt are both 'all'
                    #example:send:'Show me the figure [loss]{batches}' from phone,you will recive a jpg image of losses in batches
                    #send:'Show me the figure'，you will recive two jpg images of all metrics in batches and epochs
                    #获取图表，通过[metrics]和{level}指定参数，如果没有指定则皆默认为’all'
                    #例如，手机发送"获取图表[loss]{batches}",会收到一个jpg格式的loss随batches变化的图片
                    #手机发送"获取图表",则会得到两张图片，分别是所有指标随batch和epoch的变化
                    metrics=(self.GetMiddleStr(text,'[',']').split() if self.GetMiddleStr(text,'[',']').split() else ['all'])
                    level=(self.GetMiddleStr(text,'{','}') if self.GetMiddleStr(text,'{','}') else 'all' )
                    if level in ['all','epochs','batches']:
                        _thread.start_new_thread(self.get_fig,(level,metrics))
                    else:
                        print("Got no level,using default 'all'")
                        itchat.send("Got no level,using default 'all'", toUserName='filehelper')
                        _thread.start_new_thread(self.get_fig,())
                if any((k in text) for k in gpu_cmdlist):
                    print('\ngpuzzzzzzzzzzzzzzzzzzzzz\n')
                    sp_type_lsit=(self.GetMiddleStr(text,'[',']').split() if self.GetMiddleStr(text,'[',']').split() else ['MEMORY'])
                    av_type_list=[val for val in sp_type_lsit if val in type_list]
                    self.gpu_status(av_type_list,)
        _thread.start_new_thread(itchat.run, ())
#==============================================================================
#     
#==============================================================================
    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        for k in self.params['metrics']:
            if k in logs:
                self.logs_batches.setdefault(k, []).append(logs[k])
#==============================================================================
#                 
#==============================================================================
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch.append(epoch)
        itchat.send('Epoch'+str(epoch+1)+'/'+str(self.stopped_epoch)+' started', toUserName='filehelper')
        self.mesg = ('Epoch:'+str(epoch+1)+' ')
#==============================================================================
#         
#==============================================================================
    def on_epoch_end(self, epoch, logs=None):
        for k in self.params['metrics']:
            if k in logs:
                self.mesg+=(k+': '+str(logs[k])[:5]+' ')
                self.logs_epochs.setdefault(k, []).append(logs[k])
        try:
            itchat.send(self.mesg, toUserName='filehelper')
        except:
            itchat.auto_login(hotReload=True,enableCmdQR=True)
            itchat.dump_login_status()
            itchat.send(self.mesg, toUserName='filehelper')
        if epoch+1>=self.stopped_epoch:
            self.model.stop_training = True
        logs = logs or {}
        self.epoch.append(epoch)
        sio.savemat('logs_batches'+self.validateTitle(self.localtime)+'.mat',{'log':np.array(self.logs_batches)})
        sio.savemat('logs_epochs'+self.validateTitle(self.localtime)+'.mat',{'log':np.array(self.logs_epochs)})
        _thread.start_new_thread(self.get_fig,())
#==============================================================================
#         
#==============================================================================
    def on_train_end(self, logs=None):
        itchat.send('Train stopped at epoch'+str(self.epoch[-1]+1), toUserName='filehelper')
        
