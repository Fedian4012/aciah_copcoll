#!/usr/bin/env python
# -*- coding:Utf-8 -*- 


"""
Version basée sur GTK 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)  
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur GTK 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk3

Description : Permet de copier rapidement des morceaux de texte prédéfinis

"""

from tkinter import *
 
fenetre = Tk()

label = Label(fenetre, text="Hello World")
label.pack()

fenetre.title("Hello World")
fenetre.minsize(320,200)
fenetre.mainloop()