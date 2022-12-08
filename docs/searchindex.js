Search.setIndex({docnames:["index","plugins/lmn_auth","python/lmn_auth","python/lmn_common","python/lmn_crontab","python/lmn_devices","python/lmn_dhcp","python/lmn_docker","python/lmn_groupmembership","python/lmn_landingpage","python/lmn_linbo","python/lmn_linbo4","python/lmn_linbo_sync","python/lmn_quotas","python/lmn_session","python/lmn_settings","python/lmn_setup_wizard","python/lmn_users"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["index.rst","plugins/lmn_auth.rst","python/lmn_auth.rst","python/lmn_common.rst","python/lmn_crontab.rst","python/lmn_devices.rst","python/lmn_dhcp.rst","python/lmn_docker.rst","python/lmn_groupmembership.rst","python/lmn_landingpage.rst","python/lmn_linbo.rst","python/lmn_linbo4.rst","python/lmn_linbo_sync.rst","python/lmn_quotas.rst","python/lmn_session.rst","python/lmn_settings.rst","python/lmn_setup_wizard.rst","python/lmn_users.rst"],objects:{"aj.plugins.lmn_auth":{api:[2,0,0,"-"],views:[2,0,0,"-"]},"aj.plugins.lmn_auth.api":{LMAuthenticationProvider:[2,1,1,""],UserLdapConfig:[2,1,1,""]},"aj.plugins.lmn_auth.api.LMAuthenticationProvider":{authenticate:[2,2,1,""],authorize:[2,2,1,""],change_password:[2,2,1,""],get_isolation_gid:[2,2,1,""],get_isolation_uid:[2,2,1,""],get_ldap_user:[2,2,1,""],get_profile:[2,2,1,""]},"aj.plugins.lmn_auth.api.UserLdapConfig":{harden:[2,2,1,""],load:[2,2,1,""],save:[2,2,1,""]},"aj.plugins.lmn_auth.views":{Handler:[2,1,1,""]},"aj.plugins.lmn_auth.views.Handler":{handle_api_change_password:[2,2,1,""]},"aj.plugins.lmn_common":{api:[3,0,0,"-"],lmnfile:[3,0,0,"-"],views:[3,0,0,"-"]},"aj.plugins.lmn_common.api":{SophomorixProcess:[3,1,1,""],lmn_getSophomorixValue:[3,3,1,""]},"aj.plugins.lmn_common.api.SophomorixProcess":{run:[3,2,1,""]},"aj.plugins.lmn_common.lmnfile":{CSVLoader:[3,1,1,""],ConfigLoader:[3,1,1,""],LMNFile:[3,1,1,""],LinboLoader:[3,1,1,""],StartConfLoader:[3,1,1,""],YAMLLoader:[3,1,1,""]},"aj.plugins.lmn_common.lmnfile.LMNFile":{backup:[3,2,1,""],check_allowed_path:[3,2,1,""],detect_encoding:[3,2,1,""],hasExtension:[3,2,1,""]},"aj.plugins.lmn_common.views":{Handler:[3,1,1,""]},"aj.plugins.lmn_common.views.Handler":{handle_api_chown:[3,2,1,""],handle_api_create_dir:[3,2,1,""],handle_api_diff:[3,2,1,""],handle_api_log:[3,2,1,""],handle_api_read_setup_ini:[3,2,1,""],handle_api_remove_dir:[3,2,1,""],handle_api_remove_file:[3,2,1,""],handle_api_version:[3,2,1,""],handle_get_activeSchool:[3,2,1,""]},"aj.plugins.lmn_crontab":{manager:[4,0,0,"-"],views:[4,0,0,"-"]},"aj.plugins.lmn_crontab.manager":{CronManager:[4,1,1,""]},"aj.plugins.lmn_crontab.manager.CronManager":{load_tab:[4,2,1,""],save_tab:[4,2,1,""]},"aj.plugins.lmn_crontab.views":{Handler:[4,1,1,""]},"aj.plugins.lmn_crontab.views.Handler":{handle_api_get_crontab:[4,2,1,""],handle_api_save_crontab:[4,2,1,""]},"aj.plugins.lmn_devices":{views:[5,0,0,"-"]},"aj.plugins.lmn_devices.views":{Handler:[5,1,1,""]},"aj.plugins.lmn_devices.views.Handler":{handle_api_devices_import:[5,2,1,""],handle_api_get_devices:[5,2,1,""],handle_api_post_devices:[5,2,1,""]},"aj.plugins.lmn_dhcp":{views:[6,0,0,"-"]},"aj.plugins.lmn_dhcp.views":{Handler:[6,1,1,""]},"aj.plugins.lmn_dhcp.views.Handler":{handle_api_get_dhcp:[6,2,1,""],handle_api_register_dhcp:[6,2,1,""]},"aj.plugins.lmn_docker":{views:[7,0,0,"-"]},"aj.plugins.lmn_docker.views":{Handler:[7,1,1,""]},"aj.plugins.lmn_docker.views.Handler":{handle_api_container_stop:[7,2,1,""],handle_api_details_container:[7,2,1,""],handle_api_list_images:[7,2,1,""],handle_api_remove_image:[7,2,1,""],handle_api_resources_docker:[7,2,1,""],handle_api_which_docker:[7,2,1,""]},"aj.plugins.lmn_groupmembership":{views:[8,0,0,"-"]},"aj.plugins.lmn_groupmembership.views":{Handler:[8,1,1,""]},"aj.plugins.lmn_groupmembership.views.Handler":{handle_api_create_project:[8,2,1,""],handle_api_find_computer:[8,2,1,""],handle_api_find_group:[8,2,1,""],handle_api_find_teacher:[8,2,1,""],handle_api_find_user:[8,2,1,""],handle_api_find_usergroup:[8,2,1,""],handle_api_groupmembership_details:[8,2,1,""],handle_api_kill_project:[8,2,1,""],handle_api_list_groups:[8,2,1,""],handle_api_reset:[8,2,1,""],handle_api_set_group:[8,2,1,""],handle_api_set_members:[8,2,1,""]},"aj.plugins.lmn_landingpage":{views:[9,0,0,"-"]},"aj.plugins.lmn_linbo4":{images:[11,0,0,"-"],views:[11,0,0,"-"]},"aj.plugins.lmn_linbo4.images":{LinboImage:[11,1,1,""],LinboImageGroup:[11,1,1,""],LinboImageManager:[11,1,1,""]},"aj.plugins.lmn_linbo4.images.LinboImage":{"delete":[11,2,1,""],delete_files:[11,2,1,""],get_extra:[11,2,1,""],load_info:[11,2,1,""],rename:[11,2,1,""],save_extras:[11,2,1,""],to_dict:[11,2,1,""]},"aj.plugins.lmn_linbo4.images.LinboImageGroup":{"delete":[11,2,1,""],get_backups:[11,2,1,""],rename:[11,2,1,""]},"aj.plugins.lmn_linbo4.images.LinboImageManager":{"delete":[11,2,1,""],list:[11,2,1,""],rename:[11,2,1,""],restore:[11,2,1,""],save_extras:[11,2,1,""]},"aj.plugins.lmn_linbo4.views":{Handler:[11,1,1,""]},"aj.plugins.lmn_linbo4.views.Handler":{handle_api_linbo_restart_services:[11,2,1,""],handle_api_list_groups:[11,2,1,""]},"aj.plugins.lmn_linbo_sync":{api:[12,0,0,"-"],views:[12,0,0,"-"]},"aj.plugins.lmn_linbo_sync.api":{build_linbo_command:[12,3,1,""],devices_reader:[12,3,1,""],get_os_from_ports:[12,3,1,""],group_os:[12,3,1,""],is_port_signature_linbo:[12,3,1,""],is_port_signature_linux:[12,3,1,""],is_port_signature_windows:[12,3,1,""],last_sync:[12,3,1,""],last_sync_all:[12,3,1,""],list_workstations:[12,3,1,""],read_config:[12,3,1,""],run:[12,3,1,""],test_online:[12,3,1,""]},"aj.plugins.lmn_linbo_sync.views":{Handler:[12,1,1,""]},"aj.plugins.lmn_linbo_sync.views.Handler":{handle_api_linbo_sync:[12,2,1,""],handle_api_sync_workstation:[12,2,1,""],handle_api_workstations_online:[12,2,1,""]},"aj.plugins.lmn_quotas":{views:[13,0,0,"-"]},"aj.plugins.lmn_quotas.views":{Handler:[13,1,1,""]},"aj.plugins.lmn_quotas.views.Handler":{handle_api_apply:[13,2,1,""],handle_api_class_quotas:[13,2,1,""],handle_api_ldap_search:[13,2,1,""],handle_api_quota:[13,2,1,""],handle_api_quotas:[13,2,1,""],handle_api_save_quotas:[13,2,1,""],handle_group_quota:[13,2,1,""]},"aj.plugins.lmn_session":{views:[14,0,0,"-"]},"aj.plugins.lmn_session.views":{Handler:[14,1,1,""]},"aj.plugins.lmn_session.views.Handler":{handle_api_create_dir:[14,2,1,""]},"aj.plugins.lmn_settings":{views:[15,0,0,"-"]},"aj.plugins.lmn_settings.views":{Handler:[15,1,1,""]},"aj.plugins.lmn_settings.views.Handler":{handle_api_get_holidays:[15,2,1,""],handle_api_get_schoolsettings:[15,2,1,""],handle_api_get_subnet:[15,2,1,""],handle_api_latex_template:[15,2,1,""],handle_api_read_custom_config:[15,2,1,""],handle_api_save_custom_config:[15,2,1,""],handle_api_session_sessions:[15,2,1,""],handle_api_write_holidays:[15,2,1,""],handle_api_write_schoolsettings:[15,2,1,""],handle_api_write_subnet:[15,2,1,""]},"aj.plugins.lmn_setup_wizard":{views:[16,0,0,"-"]},"aj.plugins.lmn_setup_wizard.views":{Handler:[16,1,1,""]},"aj.plugins.lmn_setup_wizard.views.Handler":{handle_api_is_configured:[16,2,1,""],handle_api_provision:[16,2,1,""],handle_api_read_setup:[16,2,1,""],handle_api_write_setup:[16,2,1,""]},"aj.plugins.lmn_users":{views:[17,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function"},terms:{"135":12,"2222":12,"class":[1,2,3,4,5,6,7,8,11,12,13,14,15,16],"default":2,"function":[2,12],"import":5,"new":[1,2,4,6,11,13],"return":[2,3,4,5,6,7,8,11,12,13,15,16],"switch":[],"true":[3,4],"try":3,"var":16,For:2,One:12,The:[0,3,7,12],With:[],absolut:[],action:8,activ:3,activeschool:3,actual:12,adapt:[],add:[0,6,8,12],admin:[0,8],after:[],against:[1,2],all:[1,3,5,6,7,8,11,12,13,16],allow:[1,3,6],alreadi:16,angular:[2,11],angularj:0,ani:[1,3],anymor:[],api:0,appli:13,applianc:0,arg:3,argument:3,associ:11,attribut:[2,12],authent:[1,2],authentif:1,author:2,backup:[3,11],bak:3,base:0,basestr:12,basestringg:12,basic:11,befor:3,belong:12,between:3,bool:[2,3,4,6,12,16],bootstrap:12,brows:11,build:12,build_linbo_command:12,call:12,callabl:3,can:[0,1],chang:[2,11],change_password:2,check:[3,12,15,16],check_allowed_path:3,chown:3,classmethod:3,cloop:3,close:12,cmd_paramet:12,command:[3,7,12],commun:[2,3],compat:2,complet:[0,11,12],compliant:2,comput:8,conf:[11,12,13,15],config:[2,3,4,5,11,12,15,16],configload:3,configpath:12,configur:[13,15,16],conmanag:4,connect:7,connector:[3,12],constructor:3,contain:[3,7,12],container_id:7,content:[3,4,5,11],context:[2,3,4,5,6,7,8,11,12,13,14,15,16],continu:3,contribut:0,control:7,convert:[11,12],cours:[],cpu:7,creat:[1,3,8,14],credenti:2,criteria:12,cron:4,cronmanag:4,crontabconfig:4,csv:[3,5,12,15],csvloader:3,current:[2,11],custom:15,danger:13,dashboard:2,data:[4,11],date:[11,12],datetim:12,dchp:6,defin:[2,3],definit:3,delet:[7,11],delete_fil:11,delimit:3,deliv:[],deploy:0,deprec:[],descript:0,detail:[6,13],detect:3,detect_encod:3,determin:[3,15],dev:0,devic:[6,12],devices_read:12,dict:[2,3,4,6,8,11,12,13,15,16],differ:3,directori:[3,11,14],discov:11,displai:13,divers:[],doe:3,doesn:1,down:12,download:[],dpkg:3,drive:12,each:[2,6],eas:0,edit:11,email:[],enabl:2,encod:[3,15],env:[],environ:[0,8],error:[3,12,14],eventu:6,exampl:[],execut:2,exist:16,ext:3,extens:3,extra:11,fals:[2,3,11],fast:0,field:15,fieldnam:3,file:[2,3,4,5,6,11,12,15,16],filter:13,find:[0,11],finish:16,first:0,flow:3,from:[2,3,4,7,11,12,13,16],frontend:[3,4,13],gener:12,get:[2,3,4,5,6,7,8,11,12,13,15],get_backup:11,get_extra:11,get_isolation_gid:2,get_isolation_uid:2,get_ldap_us:2,get_os_from_port:12,get_profil:2,gid:[1,2],given:[3,7,11,14],global:[],globaladmin:[],globaladminss:[],goe:2,group:[3,8,11,12,13],group_o:12,groupnam:8,handl:[3,4,6,8,11,16],handle_api_appli:13,handle_api_change_password:2,handle_api_chown:3,handle_api_class_quota:13,handle_api_container_stop:7,handle_api_create_dir:[3,14],handle_api_create_project:8,handle_api_details_contain:7,handle_api_devic:[],handle_api_devices_import:5,handle_api_diff:3,handle_api_examples_prestart:[],handle_api_extra_cours:[],handle_api_extra_stud:[],handle_api_filelistimport:[],handle_api_find_comput:8,handle_api_find_group:8,handle_api_find_teach:8,handle_api_find_us:8,handle_api_find_usergroup:8,handle_api_get_crontab:4,handle_api_get_devic:5,handle_api_get_dhcp:6,handle_api_get_holidai:15,handle_api_get_schoolset:15,handle_api_get_subnet:15,handle_api_group:[],handle_api_groupmembership_detail:8,handle_api_is_configur:16,handle_api_kill_project:8,handle_api_latex_templ:15,handle_api_ldap_search:13,handle_api_linbo_restart_servic:11,handle_api_linbo_sync:12,handle_api_list_group:[8,11],handle_api_list_imag:7,handle_api_log:3,handle_api_post_devic:5,handle_api_provis:16,handle_api_quota:13,handle_api_read_custom_config:15,handle_api_read_log:[],handle_api_read_setup:16,handle_api_read_setup_ini:3,handle_api_register_dhcp:6,handle_api_remove_dir:3,handle_api_remove_fil:3,handle_api_remove_imag:7,handle_api_reset:8,handle_api_resources_dock:7,handle_api_restart:[],handle_api_save_crontab:4,handle_api_save_custom_config:15,handle_api_save_quota:13,handle_api_school_shar:[],handle_api_search_project:[],handle_api_session_sess:15,handle_api_set:[],handle_api_set_group:8,handle_api_set_memb:8,handle_api_sophomorix_globaladmin:[],handle_api_sophomorix_schooladmin:[],handle_api_sophomorix_stud:[],handle_api_sophomorix_teach:[],handle_api_stud:[],handle_api_subnet:[],handle_api_sync_workst:12,handle_api_teach:[],handle_api_users_appli:[],handle_api_users_check:[],handle_api_users_get_class:[],handle_api_users_globaladmins_cr:[],handle_api_users_password:[],handle_api_users_print:[],handle_api_users_print_download:[],handle_api_users_print_individu:[],handle_api_users_schooladmins_cr:[],handle_api_users_test_password:[],handle_api_vers:3,handle_api_which_dock:7,handle_api_workstations_onlin:12,handle_api_write_holidai:15,handle_api_write_schoolset:15,handle_api_write_setup:16,handle_api_write_subnet:15,handle_custom:[],handle_custom_csv:[],handle_custom_multi_remov:[],handle_custom_mutli_add:[],handle_get_activeschool:3,handle_group_quota:13,handle_set_proxy_address:[],handler:[2,3,4,5,6,7,8,11,12,13,14,15,16],harden:2,hasextens:3,hash:7,have:1,header:[],here:3,hide:8,his:[2,11],holidai:15,host:[7,12],hostnam:12,http:[],http_context:[2,3,4,5,6,7,8,11,12,13,14,15,16],httpcontext:[2,3,4,5,6,7,8,11,12,13,15,16],ident:2,ignor:[3,14],ignoreerror:3,imag:[7,12],image_id:7,individu:[],info:[11,12],inform:[2,3,7,8,12,13],ini:[3,16],initi:2,inject:12,inspect:7,instal:[0,3,16],integ:[2,3,12],integr:0,invok:3,is_port_signature_linbo:12,is_port_signature_linux:12,is_port_signature_window:12,isol:2,its:[3,11],job:4,join:8,json:[3,7],jsonpath:3,keep:[2,3],kei:[3,12,13],keyword:3,kill:8,kvm:0,kwarg:3,last:12,last_sync:12,last_sync_al:12,latex:15,launch:[5,12,16],ldap:[1,2,8,13],learn:0,leas:6,lib:16,like:[],limit:[1,13],linbo4:11,linbo:3,linbo_path:11,linboimag:11,linboimagegroup:11,linboimagemanag:11,linboload:3,line:[3,7,12],linux:12,linuxmust:[2,3,8,16],list:[0,3,7,8,11,12,13,15],list_workst:12,lmauthenticationprovid:2,lmn_cron:[],lmn_get_school_configpath:[],lmn_getsophomorixvalu:3,load:[2,4,5,7,11],load_info:11,load_tab:4,log:3,login:[8,13],magic:3,mai:3,maillist:8,manag:[0,1,2,8,11,13],manipul:3,mean:1,member:8,memori:7,meta:3,method:[3,6,8],mode:[2,3,5,15],modifi:3,modul:[2,4,6,7,12,15],more:[],multi:[],multicast:11,multischool:[],name:[3,8,11,12],necessari:11,need:[0,11],net:[0,2],network:0,new_nam:11,new_password:2,newfil:[],newli:[],nmap:12,none:[3,7,11,13],number:[3,12],object:[2,3,4,11],off:12,offici:0,offset:3,old:2,onc:1,one:[7,13],onli:[0,1,11,12],onlin:12,open:12,openport:12,oper:8,option:[3,8],order:[0,1],otherwis:2,out:12,output:3,overrid:3,owner:[2,3,8],packag:3,page:0,panel:0,param:4,paramet:[2,3,4,5,6,7,8,11,12,13,15,16],pars:[2,3],part:[0,3],partial:[],particularli:0,pass:3,passwd:2,password:2,path:[2,3,11,12,14],pdf:[],per:[7,13],perform:1,permiss:[1,2],permit:0,person:2,plugin:0,port:12,post:[7,8],postsync:[],prepar:[0,2,11,13],prestart:[],print:15,printer:8,process:[0,2,3,16],profil:[1,2],project:[0,3,8,13],provid:[0,1,2],proxmox:0,proxyaddress:[],python:0,queri:[3,13],quiet:3,quota:[],read:[2,3,5,6,12,15,16],read_config:12,reason:3,recursiverli:11,refer:0,regist:[5,6,13],remot:12,remov:[3,7,8,11],renam:11,repres:3,requir:[],reset:8,respect:3,restart:11,restor:11,restrict:1,result:[3,8],retriev:7,right:2,role:15,root:2,rtype:4,run:[3,5,12],samba:[1,13],same:1,save:[2,3,4,11,15],save_extra:11,save_tab:4,scheme:[2,3],school:[0,3,12,13,15],schooladmin:[],schooladminss:[],script:[],search:[3,8],secur:3,select:[],self:[2,7],sensit:3,sent:[7,12],sequenti:3,server:[0,1],servic:[11,16],session:2,set:[12,16],setup:3,share:13,shortnam:[],should:3,simpl:7,simul:3,some:[0,7,11,12],sophomorix:[2,3,13,15],sophomorixcommand:3,sophomorixprocess:3,sort:6,sourc:[2,3,4,5,6,7,8,11,12,13,14,15,16],specif:0,specifi:[8,13],ssh:7,standard:3,start:[7,11,12],startconfload:3,stat:7,state:12,statu:[12,13],still:[],stop:7,store:[4,7],str:11,string:[2,3,4,5,12,13,15],student:[],style:13,subclass:3,subnet:15,subprocess:7,success:[3,6,13],successful:[4,12],synchronis:12,system:5,taken:3,target:3,task:1,teacher:8,templat:15,test:[0,2,7,12,16],test_onlin:12,thi:[0,1,2,3,6],thread:3,through:[2,3,4,6,12,13],time:12,timestamp:[3,11],tmp:16,to_dict:11,tool:[3,8],torrent:11,tree:[2,11,13],tupl:[6,8],two:3,type:[2,3,4,5,6,7,8,11,12,13,15,16],uid:[1,2],unknown:12,updat:[],use:[0,7,12],used:[1,2,3],useful:[],user:[1,2,3,4,8,12,13],userconfig:2,userldapconfig:2,usernam:[2,13],using:[3,15],utf:15,valu:[2,3,12,13],variabl:11,version:[3,7],view:1,want:0,warn:13,webui:15,welcom:0,when:6,whether:12,which:0,whole:[0,3,11,12],window:12,wizard:3,worker:[1,2,3],workstat:12,write:[2,5,15,16],written:0,xcp:0,yaml:[2,3,15],yamlload:3,yml:15,you:[0,3]},titles:["Linuxmuster-webui7\u2019s developer documentation","Plugin lmn_auth","API: aj.plugins.lmn_auth","API: aj.plugins.lmn_common","API: aj.plugins.lmn_crontab","API: aj.plugins.lmn_devices","API: aj.plugins.lmn_dhcp","API: aj.plugins.lmn_docker","API: aj.plugins.lmn_groupmembership","API: aj.plugins.lmn_landingpage","API: aj.plugins.lmn_linbo","API: aj.plugins.lmn_linbo4","API: aj.plugins.lmn_linbo_sync","API: aj.plugins.lmn_quotas","API: aj.plugins.lmn_session","API: aj.plugins.lmn_settings","API: aj.plugins.lmn_setup_wizard","API: aj.plugins.lmn_users"],titleterms:{about:0,ajenti:0,api:[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],auth:2,common:3,crontab:4,develop:0,devic:5,dhcp:6,docker:7,document:0,groupmembership:8,imag:11,land:9,linbo:[10,11,12],linuxmust:0,lmn:[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],lmn_auth:[1,2],lmn_common:3,lmn_crontab:4,lmn_devic:5,lmn_dhcp:6,lmn_docker:7,lmn_groupmembership:8,lmn_landingpag:9,lmn_linbo4:11,lmn_linbo:10,lmn_linbo_sync:12,lmn_quota:13,lmn_session:14,lmn_set:15,lmn_setup_wizard:16,lmn_user:17,lmnfile:3,manag:4,page:9,plugin:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],quota:13,session:14,set:15,setup:16,sync:12,user:17,view:[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],webui7:0,wizard:16}})