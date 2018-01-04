#!/usr/bin/env python3
#-*- coding:utf-8 -*-

###############################################################
# -- Tscan Wrapper script for CLAM --
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
###############################################################


#This script will be called by CLAM and will run with the current working directory set to the specified project directory
from __future__ import print_function

#import some general python modules:
import sys
import os
import shutil
import glob
import signal

#import CLAM-specific modules. The CLAM API makes a lot of stuff easily accessible.
import clam.common.data
import clam.common.status


#this script takes three arguments from CLAM: $DATAFILE $STATUSFILE $OUTPUTDIRECTORY  (as configured at COMMAND= in the service configuration file)
datafile = sys.argv[1]
statusfile = sys.argv[2]
inputdir = sys.argv[3]
outputdir = sys.argv[4]
TSCANDIR = sys.argv[5]
ALPINOHOME = sys.argv[6]

#Obtain all data from the CLAM system (passed in $DATAFILE (clam.xml))
clamdata = clam.common.data.getclamdata(datafile)

#You now have access to all data. A few properties at your disposition now are:
# clamdata.system_id , clamdata.project, clamdata.user, clamdata.status , clamdata.parameters, clamdata.inputformats, clamdata.outputformats , clamdata.input , clamdata.output

clam.common.status.write(statusfile, "Starting...")

if not 'word_freq_lex' in clamdata:
    print("Missing parameter: word_freq_lex", file=sys.stderr)
    sys.exit(2)
if not 'lemma_freq_lex' in clamdata:
    print("Missing parameter: lemma_freq_lex", file=sys.stderr)
    sys.exit(2)
if not 'top_freq_lex' in clamdata:
    print("Missing parameter: top_freq_lex", file=sys.stderr)
    sys.exit(2)


def load_custom_wordlist(configfile, inputdir, tscan_name, inputtemplate, default_location=None):
    """This allows custom word lists. Does require to specify the full path to the files."""
    wordlist = None

    for inputfile in clamdata.inputfiles(inputtemplate):
        wordlist = inputdir + inputfile.filename
        break
    else:
        # When no inputfile is found, revert to the default (if there is one)
        if default_location:
            wordlist = TSCANDIR + default_location

    # Write the wordlist to the config file
    if wordlist:
        configfile.write(tscan_name + "=\"" + wordlist + "\"\n")

#Write configuration file

f = open(outputdir + '/tscan.cfg', 'w')
if 'useAlpino' in clamdata and clamdata['useAlpino'] == 'yes':
    f.write("useAlpinoServer=1\n")
    f.write("useAlpino=1\n")
else:
    f.write("useAlpinoServer=0\n")
    f.write("useAlpino=0\n")
if 'useWopr' in clamdata and clamdata['useWopr'] == 'yes':
    f.write("useWopr=1\n")
else:
    f.write("useWopr=0\n")
if 'sentencePerLine' in clamdata and clamdata['sentencePerLine'] == 'yes':
    f.write("sentencePerLine=1\n")
else:
    f.write("sentencePerLine=0\n")

f.write("useLsa=0\n")  # LSA is disabled
f.write("surprisalPath=\"" + TSCANDIR + "\"\n")
f.write("styleSheet=\"tscanview.xsl\"\n")

if 'rarityLevel' in clamdata:
    raritylevel = clamdata['rarityLevel']
else:
    raritylevel = 4

if 'overlapSize' in clamdata:
    overlapsize = clamdata['overlapSize']
else:
    overlapsize = 50

if 'frequencyClip' in clamdata:
    freqclip = clamdata['frequencyClip']
else:
    freqclip = 99

if 'mtldThreshold' in clamdata:
    mtldthreshold = clamdata['mtldThreshold']
else:
    mtldthreshold = 0.720

f.write("rarityLevel=" + str(raritylevel) + "\n")
f.write("overlapSize=" + str(overlapsize) + "\n")
f.write("frequencyClip=" + str(freqclip) + "\n")
f.write("mtldThreshold=" + str(mtldthreshold) + "\n")

f.write("configDir=" + TSCANDIR + "/data\n")
f.write("verb_semtypes=\"verbs_semtype.data\"\n")
f.write("general_nouns=\"general_nouns.data\"\n")
f.write("general_verbs=\"general_verbs.data\"\n")
f.write("adverbs=\"adverbs.data\"\n")

# 20160802: This allows a completely dcustom classification.
load_custom_wordlist(f, inputdir, "my_classification", "myclassification")
# 20150316: This allows custom adjective classification.
load_custom_wordlist(f, inputdir, "adj_semtypes", "adjclassification", "/data/adjs_semtype.data")
# 20141121: This allows a custom noun classification.
load_custom_wordlist(f, inputdir, "noun_semtypes", "nounclassification", "/data/nouns_semtype.data")
# 20150203: This allows custom intensifying words.
load_custom_wordlist(f, inputdir, "intensify", "intensify", "/data/intensiveringen.data")

f.write("word_freq_lex=\"" + clamdata['word_freq_lex'] + "\"\n")  # freqlist_staphorsius_CLIB_words.freq
f.write("lemma_freq_lex=\"" + clamdata['lemma_freq_lex'] + "\"\n")  # freqlist_staphorsius_CLIB_lemma.freq
f.write("staph_word_freq_lex=\"freqlist_staphorsius_CLIB_words.freq\"\n")  # freqlist_staphorsius_CLIB_words.freq
f.write("top_freq_lex=\"" + clamdata['top_freq_lex'] + "\"\n")  # freqlist_staphorsius_CLIB_words.freq

f.write("voorzetselexpr=\"voorzetseluitdrukkingen.txt\"\n")
f.write("afkortingen=\"afkortingen.lst\"\n")
f.write("temporals=\"temporal_connectors.lst\"\n")
f.write("opsom_connectors_wg=\"opsom_connectors_wg.lst\"\n")
f.write("opsom_connectors_zin=\"opsom_connectors_zin.lst\"\n")
f.write("contrast=\"contrast_connectors.lst\"\n")
f.write("compars=\"compar_connectors.lst\"\n")
f.write("causals=\"causal_connectors.lst\"\n")
f.write("causal_situation=\"causaliteit.txt\"\n")
f.write("space_situation=\"ruimte.txt\"\n")
f.write("time_situation=\"tijd.txt\"\n")
f.write("emotion_situation=\"emoties.txt\"\n")

prevalence = 'nl'
if 'prevalence' in clamdata:
    prevalence = clamdata['prevalence']
f.write("prevalence=\"prevalence_" + prevalence + ".data\"\n")


f.write("[[frog]]\n")  # Frog server should already be runnning, start manually
f.write("port=7001\n")
f.write("host=127.0.0.1\n\n")

f.write("[[wopr]]\n")
f.write("port_fwd=7020\n")
f.write("host_fwd=127.0.0.1\n\n")
f.write("port_bwd=7002\n")
f.write("host_bwd=127.0.0.1\n\n")

f.write("[[alpino]]\n")
f.write("port=7003\n")
f.write("host=127.0.0.1\n")

f.write("[[lsa_words]]\n")
f.write("port=7004\n")
f.write("host=127.0.0.1\n")

f.write("[[lsa_docs]]\n")
f.write("port=7005\n")
f.write("host=127.0.0.1\n")


f.close()


#collect all input files
inputfiles = []
for inputfile in clamdata.inputfiles('textinput'):
    if '"' in str(inputfile):
        clam.common.status.write(statusfile, "Failed, filename has a &quot;, illegal!", 100)  # status update
        sys.exit(2)
    inputtemplate = inputfile.metadata.inputtemplate
    inputfiles.append(str(inputfile))


def sigterm_handler():
    #collect output
    clam.common.status.write(statusfile, "Postprocessing after forceful abortion", 90)  # status update
    for inputfile in inputfiles:
        os.rename(inputfile + '.tscan.xml', outputdir + '/' + os.path.basename(inputfile).replace('.txt.tscan', '').replace('.txt', '') + '.xml')

    #tscan writes CSV file in input directory, move:
    os.system("mv -f " + inputdir + "/*.csv " + outputdir)

    os.system("cat " + outputdir + "/*.words.csv | head -n 1 > " + outputdir + "/total.word.csv")
    os.system("cat " + outputdir + "/*.paragraphs.csv | head -n 1 > " + outputdir + "/total.par.csv")
    os.system("cat " + outputdir + "/*.sentences.csv | head -n 1 > " + outputdir + "/total.sen.csv")
    os.system("cat " + outputdir + "/*.document.csv | head -n 1 > " + outputdir + "/total.doc.csv")

    for f in glob.glob(outputdir + "/*.words.csv"):
        os.system("sed 1d " + f + " >> " + outputdir + "/total.word.csv")
    for f in glob.glob(outputdir + "/*.paragraphs.csv"):
        os.system("sed 1d " + f + " >> " + outputdir + "/total.par.csv")
    for f in glob.glob(outputdir + "/*.sentences.csv"):
        os.system("sed 1d " + f + " >> " + outputdir + "/total.sen.csv")
    for f in glob.glob(outputdir + "/*.document.csv"):
        os.system("sed 1d " + f + " >> " + outputdir + "/total.doc.csv")
    sys.exit(5)

signal.signal(signal.SIGTERM, sigterm_handler)

shutil.copyfile(TSCANDIR + "/view/tscanview.xsl", outputdir + "/tscanview.xsl")

#pass all input files at once
clam.common.status.write(statusfile, "Processing " + str(len(inputfiles)) + " files, this may take a while...", 10)  # status update
ref = os.system('ALPINO_HOME="' + ALPINOHOME + '" TCL_LIBRARY="' + ALPINOHOME + '/create_bin/tcl8.5" TCLLIBPATH="' + ALPINOHOME + '/create_bin/tcl8.5" tscan --config=' + outputdir + '/tscan.cfg ' + ' '.join(['"' + x + '"' for x in inputfiles]))

#collect output
clam.common.status.write(statusfile, "Postprocessing", 90)  # status update
for inputfile in inputfiles:
    try:
        os.rename(inputfile + '.tscan.xml', outputdir + '/' + os.path.basename(inputfile).replace('.txt.tscan', '').replace('.txt', '') + '.xml')
    except FileNotFoundError:
        print("Expected output file " + inputfile + ".tscan.xml not created, something went wrong earlier?", file=sys.stderr)

if ref != 0:
    clam.common.status.write(statusfile, "Failed", 90)  # status update

#tscan writes CSV file in input directory, move:
os.system("mv -f " + inputdir + "/*.csv " + outputdir)

#write the csv headers to a file with all results ('total.<type>.csv')
os.system("cat " + outputdir + "/*.words.csv | head -n 1 > " + outputdir + "/total.word.csv")
os.system("cat " + outputdir + "/*.paragraphs.csv | head -n 1 > " + outputdir + "/total.par.csv")
os.system("cat " + outputdir + "/*.sentences.csv | head -n 1 > " + outputdir + "/total.sen.csv")
os.system("cat " + outputdir + "/*.document.csv | head -n 1 > " + outputdir + "/total.doc.csv")

#move the contents of the files to the total files
for f in glob.glob(outputdir + "/*.words.csv"):
    os.system("sed 1d \"" + f + "\" >> " + outputdir + "/total.word.csv")
for f in glob.glob(outputdir + "/*.paragraphs.csv"):
    os.system("sed 1d \"" + f + "\" >> " + outputdir + "/total.par.csv")
for f in glob.glob(outputdir + "/*.sentences.csv"):
    os.system("sed 1d \"" + f + "\" >> " + outputdir + "/total.sen.csv")
for f in glob.glob(outputdir + "/*.document.csv"):
    os.system("sed 1d \"" + f + "\" >> " + outputdir + "/total.doc.csv")

#A nice status message to indicate we're done
clam.common.status.write(statusfile, "Done", 100)  # status update

sys.exit(ref)  # non-zero exit codes indicate an error and will be picked up by CLAM as such!
