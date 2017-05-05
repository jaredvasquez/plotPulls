import os
from ROOT import *

gROOT.SetBatch(kTRUE)

def iterate( args ):
  iter = args.createIterator()
  var = iter.Next()
  while var:
    yield var
    var = iter.Next()

# collect NP pulls from workspace
tf = TFile('ucmles/WS-HGam-muGlobal.root')
ws = tf.Get('combWS')
mc = ws.obj('ModelConfig')
ws.loadSnapshot('ucmles')

# Load ATLAS Style
gROOT.LoadMacro("AtlasStyle.C")
gROOT.LoadMacro("AtlasUtils.C")
gROOT.LoadMacro("AtlasLabels.C")
SetAtlasStyle()

# set margin sizes
gStyle.SetPadTopMargin(0.08)
gStyle.SetPadRightMargin(0.05)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetPadLeftMargin(0.40)

gStyle.SetTitleXOffset(1.0)
gStyle.SetTitleYOffset(1.4)
gStyle.SetLabelSize(0.035,"xy")

pulls = {}
for NP in iterate(mc.GetNuisanceParameters()):
  NPname = NP.GetName()
  if not 'ATLAS_' in NPname: continue
  pulls[NPname] = [ NP.getVal(), NP.getError(), -NP.getError() ]

# function to draw errors in background
def drawBGErrors( numNPs ):
  mbox = TBox()
  mbox.SetFillColor( kYellow )
  mbox.DrawBox(-2,-1.5,2,numNPs+0.5)
  mbox.SetFillColor( kGreen )
  mbox.DrawBox(-1,-1.5,1,numNPs+0.5)

  mline = TLine()
  mline.SetLineWidth(2)
  mline.SetLineStyle(7)
  mline.SetLineColor(kGreen)
  mline.DrawLine(-1.5,-1.5,-1.5,numNPs+0.5)
  mline.DrawLine(+1.5,-1.5,+1.5,numNPs+0.5)
  mline.SetLineColor(kGreen+1)
  mline.DrawLine(0.,-1.5,0.,numNPs+0.5)

# Define function to return TGraph of pulls
plotNames = {
    "JETS": ["JET_","MET_"],
    "MASS": ["SCALE_","RESOLUTION_"],
    "LEPS": ["PH_","EL_","MUON_","Hgg_Trigger","lumi_","PRW"],
    "SPUR": ["Hgg_Bias_"],
    "FTAG": ["FT_"],
     "PDF": ["PDF4LHC"],
  "THEORY": ["QCDscale_","BR_","HFcontent","UEPS"],
}

can = TCanvas("can","",800,1200)
for plotName in plotNames:

  filterWords = plotNames[plotName]
  # Get List of NPs
  NPnames = []
  for NPname in pulls:
    for filt in filterWords:
      if filt in NPname:
        NPnames.append(NPname)
  NPnames.sort(reverse=True)

  # Define histogram and tgraphs
  xmax = 2.5
  xmin = -xmax
  h = TH2F("hist",";#hat{#theta} - #theta_{0}",10,xmin,xmax,len(NPnames)+2,-1.5,len(NPnames)+0.5)
  tg_pulls = TGraphAsymmErrors()
  tg_pulls.SetMarkerStyle(20)

  iNP=0
  for NPname in NPnames:

    # Fix Naming
    name = NPname
    name = name.replace('ATLAS_','')
    name = name.replace('_1NPCOR_PLUS_UNCOR','')
    name = name.replace('calibration','calib')
    name = name.replace('extrapolation','extrap')

    # Label Axis
    h.GetYaxis().SetBinLabel( iNP+2, name )

    # Get Pull Parameters
    pull = pulls[NPname]
    mean = float(pull[0])
    ErrorLo = abs(float(pull[1]))
    ErrorHi = abs(float(pull[2]))

    tg_pulls.SetPoint( iNP, mean, iNP )
    tg_pulls.SetPointError( iNP, ErrorLo, ErrorHi, 0., 0. )
    iNP += 1

    del pulls[NPname]

  h.Draw("HIST")
  drawBGErrors(len(NPnames))
  h.Draw("HIST AXIS SAME")
  tg_pulls.Draw("P SAME")

  ATLASLabel(0.32,0.94,"Internal");
  myText( 0.675, 0.94, kBlack, "#sqrt{s} = 13 TeV, 36.1 fb^{-1}", 0.035 )

  can.Update()
  os.system('mkdir -p plots/png')
  os.system('mkdir -p plots/pdf')
  #os.system('mkdir -p plots/eps')
  #os.system('mkdir -p plots/macros')

  can.SaveAs("plots/png/pulls_%s.png"%plotName)
  can.SaveAs("plots/pdf/pulls_%s.pdf"%plotName)
  #can.SaveAs("plots/eps/pulls_%s.eos"%plotName)
  #can.SaveAs("plots/macros/pulls_%s.C"%plotName)

# Check that I didn't miss something
print '\n'
print 'Missing NPs:'
print '-'*25
for NP in pulls:
  print NP
print ''
