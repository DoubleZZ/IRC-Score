# -*- coding: utf-8 -*-
# Programme de comptage de points
#
# Par Double Z.
# =============================================

import irclib
import ircbot

nick = "VincentLagaf"
description = "Bot de comptage de points en Python via ircBot (V2)"
room = "#riffTest"
server = "irc.worldnet.net"
port = 6667
utilisateurs = ["DoubleZ","Herondil"]

score = {}

#Fonction vérifiant la syntaxe des commandes entrées, renvoie une erreur et interromp la commande en cours
def verifCommand(s, c, parameters) :
  global numbers
  global isParamNumber
  
  numbers = 0
  isParamNumber = False
  
  if parameters[0] in ["!add","!sub","!set"] :
    if len(parameters) == 1 :
      s.privmsg(c,"Erreur : La commande requiert d'inclure des pseudos ainsi que les points si necessaire")
      s.privmsg(c,"USAGE : " + parameters[0] + " pseudo(s) (point(s))")
      s.privmsg(c,"USAGE : " + parameters[0] + " pseudo(s) point(s) pseudo(s) point(s)")
      return False
      
    if len(parameters) == 2 and parameters[1].isdigit() :
      s.privmsg(c,"Erreur : Aucun pseudo(s) n'a été entrée dans la commande")
      return False

    for p in parameters :
      if p.isdigit() and isParamNumber :
	s.privmsg(c,"Erreur : La commande ne devrait pas avoir plusieurs nombres d'affilés")
	return False
      
      if p.isdigit() :
	numbers += 1
	isParamNumber = True
      else :
	isParamNumber = False
      
    if not isParamNumber and numbers > 0 :
      s.privmsg(c,"Erreur : La commande n'indique pas le nombre de points a allouer pour le dernier groupe")
      return False
      
    if parameters[0] == "!set" and not isParamNumber and numbers == 0 :
      s.privmsg(c,"Erreur : La commande requiert un nombre de points a définir")
      return False
      
  if parameters[0] in ["!modo","!nomodo"]:
    if len(parameters) == 1 :
      s.privmsg(c,"Erreur : La commande requiert d'inclure un pseudo")
      s.privmsg(c,"USAGE : " + parameters[0] + " pseudo")
      return False
      
    if len(parameters) > 2 :
      s.privmsg(c,"Erreur : La commande ne demande qu'un pseudo")
      return False
      
  #Sinon tout va bien  
  return True

def setPoints(mode,name,points):
  if mode == "!set" :
    score[name] = points
    
  if mode == "!add" :
    try :
      score[name] += points
    except :
      score[name] = points
      
  if mode == "!sub" :
    try :
      score[name] -= points
    except :
      score[name] = - points

class BotScore(ircbot.SingleServerIRCBot):
  def __init__(self):
    global nick
    global room
    global server
    global port
    
    ircbot.SingleServerIRCBot.__init__(self, [(server, port)],nick,description)
    
  def on_welcome(self,serv,ev):
    serv.join(room)
    
  def on_pubmsg(self,serv,ev):
    global score
    auteur = irclib.nm_to_n(ev.source())
    canal = ev.target()
    message = ev.arguments()[0].split(" ")
    
    #Verification d'une commande correcte
    if verifCommand(serv, canal, message):
      #Ajout d'un modo
      if message[0] == "!modo" :
	utilisateurs.append(message[1])
	serv.privmsg(canal,message[1] + " peut maintenant utiliser les commandes du bot")
      
      #Suppression d'un modo
      if message[0] == "!nomodo" :
	for index,name in enumerate(utilisateurs):
	  if name == message[1]:
	    utilisateurs.pop(index)
	    serv.privmsg(canal,message[1] + " ne peut plus utiliser les commandes du bot")
      
      #Affichage du score
      if message[0] == "!score" :
	if auteur in utilisateurs :
	  for nom in sorted(score.items(),key=lambda d:d[1],reverse=False) :
	    serv.privmsg(canal,nom[0] + " = " + str(nom[1]) +" points")
		
	else :
	  for nom in sorted(score.items(),key=lambda d:d[1],reverse=False) :
	    serv.privmsg(auteur,nom[0] + " = " + str(nom[1]) +" points")
      
      #Distribution des points
      if message[0] in ["!add","!sub","!set"] :
	groupe = []
	for index,param in enumerate(message[1:]) :
	  if not param.isdigit() :
	    groupe.append(param)
	  if param.isdigit() or (index == len(message[1:])-1 and numbers == 0 and isParamNumber == False) :
	    for name in groupe :
	      if index == len(message[1:])-1 and numbers == 0 and isParamNumber == False :
		param = "1"
	      setPoints(message[0],name,int(param))
	
	    #Conjugaison
	    if len(groupe) > 1 :
	      pluriel = True
	    else :
	      pluriel = False
	      
	    #Construction de la phrase
	    sentence = ""
	    for index,name in enumerate(groupe) :
	      sentence += name
	      if index == len(groupe)-2 :
		sentence += " et "
	      elif index != len(groupe)-1 :
		sentence =", "
		  
	    if message[0] == "!set" :
	      if pluriel :
		verbe = "ont maintenant"
	      else :
		verbe = "a maintenant"
	    if message[0] == "!add" :
	      verbe = "gagne" + "nt chacuns" * pluriel
	    if message[0] == "!sub" :
	      verbe = "perd" + "ent chacuns" * pluriel
	  
	    sentence += " " + verbe + " " + param + " point(s)"
	    
	    groupe = []
		
	    #Envoie du message
	    serv.privmsg(canal,sentence)
      
      #DEBUG
      #serv.privmsg(canal,str(numbers) + " " + str(isParamNumber))
    
if __name__ == "__main__":
  BotScore().start()
