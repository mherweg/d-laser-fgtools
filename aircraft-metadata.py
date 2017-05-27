#!/usr/bin/python3
# -*- coding: utf-8 -*-

#(c) 2015 d-laser  http://wiki.flightgear.org/User:Laserman
# --------------------------------------------------------------------------
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# --------------------------------------------------------------------------

#input looks like this:

#<li class="Mono-moteur Hélice Canard Bi-plans France">
#<a href="http://helijah.free.fr/flightgear/les-appareils/14bis/appareil.htm">
#<span class="name">14 Bis</span>
#--
#<li class="Mono-moteur Hélice Mono-plan Hydravion France">
#<a href="http://helijah.free.fr/flightgear/les-appareils/late29/appareil.htm">
#<span class="name">Late 29</span>

# get the input from here:
# http://helijah.free.fr/flightgear/framehangarfr.htm



#output files shall be includend in each aircraft's set file



import re

pattern_tag = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern_name = re.compile(r'<span class="name">\w*</span>$')

all_tags=[]

input_filename = "filtered.txt"
infile = open(input_filename, 'r')


tags_fr = ['Multi-moteurs', 'Hélice', 'Hydravion', 'Mono-plan', 'Géant',    'Etats-Unis', 'Mono-moteur', 'ULM'     , 'Bi-plans', 'France', 'Bi-moteurs', 'Militaire', 'Canard', 'Prototype', 'Allemagne', 'Tri-moteurs', 'Quadri-moteurs', 'WW1', 'Réacteur', 'WW2', 'Racer', 'Angleterre', 'Hélicoptère', 'Convertible', 'Suède', 'Imaginaire', 'Autres', 'Italie', 'Ukraine', 'Russie', 'Dual-control', 'Tchécoslovaquie', 'Japon', 'Canada', 'Belgique', 'Liner', 'Voiture', 'Planeur', 'Autriche', 'Australie', 'Fusée', 'Suisse', 'Brésil']

tags_en = ['multi-engine','prop','seaplane','monoplane','giant','United States','single engine','ultralight', 'biplane', 'France','twin engine', 'military','canard','prototype','Germany' , 'triple engine', 'quad engine',     'WW1', 'jet' , 'WW2',      'racer' ,   'UK' , 'helicopter',      'convertable', 'Sweden'  ,'fictional', 'other', 'Italy', 'Ukraine', 'Russia', 'dual control',  'Czech Republic', 'Japan'  , 'Canada', 'Belgium', 'airliner', 'car', 'Glider',  'Austria', 'Australia', 'spacecraft', 'Switzerland', 'Brazil']



def to_en(tag):
    if (tag in tags_fr):
        index = tags_fr.index(tag)
        tag_en = tags_en[index]
    return(tag_en)
    
def ac_write(name, tags):
    # create a file for each aircraft
    f = open("out/"+name, 'w')
    f.write ("<tags>\n")
    for tag in tags:
        if (tag in all_tags):
            pass
        else:
            all_tags.append(tag)
            #print(all_tags)
            #print(tag + " added.")
        tag_en = to_en(tag)
        f.write("    <tag>" + tag_en + "</tag>\n")
    f.write ("</tags>\n")
    f.close()


for line in infile:
    
    #line = infile.read()
    line = line.strip()
  
    if line.startswith('<li class="') :
        res = re.search(r'<li class="(.*)">',line)
        tags = res.group(1)
        
        tags = tags.split(" ")
        
        #pong = 0
        
        #<li class="Mono-moteur Hélice Canard Bi-plans France">
        #print (tags)
   
    if line.startswith('<span class="name">'):
        #result = pattern_name.match(line)
        res = re.search(r'<span class="name">(.*)</span>',line)
        name = res.group(1)
    
        #print(name, tags)
        ac_write(name, tags)
        
        
#print (all_tags)
print ("done")
