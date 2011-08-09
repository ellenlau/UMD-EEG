#!/usr/bin/python

from numpy import array, flatnonzero, arange, shape, zeros, ones
from struct import unpack, calcsize
import tables
import sys
import os.path
try:
    import psyco
    psyco.full()
except:
    pass

class Event():
    count = 0
    def __init__(self):
        self.event_id = Event.count
        Event.count += 1


class Electrode():
    def __repr__(self):
        return self.label


class CNTData():
    """A class for reading Neuroscan .cnt files."""
    
    def __init__(self, filename):
        self.filename = filename
        self.file = open(self.filename, 'rb')
        
        self.load_setup()
        self.load_electrodes()
        
        self.save_data()
        
    def get(self, ctype, size=1):
        """Reads and unpacks binary data into the desired ctype."""
        if size == 1:
            size = ''
        else:
            size = str(size)
        
        chunk = self.file.read(calcsize(size + ctype))
        read_chunk = unpack(size + ctype, chunk)
        if len(read_chunk) == 1:
            return read_chunk[0]
        else:
            return read_chunk
    
    def create_h5(self):
        """Creates an empty HDF5 file based on the name of the input file."""
        h5_filename = os.path.splitext(cnt_filename)[0] + ".h5"
        self.h5 = tables.openFile(h5_filename, mode="w", title="EEG data")
    
    def load_electrodes(self):
        """Loads electrode data from CNT file."""
        
        # Electrode data starts at 900.
        self.file.seek(900)
        self.electrodes = [self.get_electrode() for _ in xrange(self.info["nchannels"])]
                
    def get_electrode(self):
        "Reads electrode information from CNT header."
        
        electrode = Electrode()
        electrode.label          = self.get('10s').strip('\x00')
        electrode.reference      = self.get('?')
        electrode.skip           = self.get('?')
        electrode.reject         = self.get('?')
        electrode.display        = self.get('?')
        electrode.bad            = self.get('?')
        electrode.n              = self.get('H')
        electrode.avg_reference  = self.get('s')
        electrode.clipadd        = self.get('s')
        electrode.x_coord        = self.get('f')
        electrode.y_coord        = self.get('f')
        electrode.veog_wt        = self.get('f')
        electrode.veog_std       = self.get('f')
        electrode.snr            = self.get('f')
        electrode.heog_wt        = self.get('f')
        electrode.heog_std       = self.get('f')
        electrode.baseline       = self.get('h')
        electrode.filtered       = self.get('s')
        electrode.fsp            = self.get('s')
        electrode.aux1_wt        = self.get('f')
        electrode.aux1_std       = self.get('f')
        electrode.sensitivity    = self.get('f')
        electrode.gain           = self.get('s')
        electrode.hipass         = self.get('s')
        electrode.lopass         = self.get('s')
        electrode.page           = self.get('B')
        electrode.size           = self.get('B')
        electrode.impedance      = self.get('B')
        electrode.physicalchnl   = self.get('B')
        electrode.rectify        = self.get('s')
        electrode.calib          = self.get('f')
        
        return electrode
    
    def load_setup(self):
        """Loads CNT metadata from header."""
        
        self.info = {}
        
        self.file.seek(0)
        self.info["rev"]               = self.get('12s')
        self.info["nextfile"]          = self.get('l')
        self.info["prevfile"]          = self.get('L')
        self.info["type"]              = self.get('b')
        self.info["id"]                = self.get('20s')
        self.info["oper"]              = self.get('20s')
        self.info["doctor"]            = self.get('20s')
        self.info["referral"]          = self.get('20s')
        self.info["hospital"]          = self.get('20s')
        self.info["patient"]           = self.get('20s')
        self.info["age"]               = self.get('h')
        self.info["sex"]               = self.get('s')
        self.info["hand"]              = self.get('s')
        self.info["med"]               = self.get('20s')
        self.info["category"]          = self.get('20s')
        self.info["state"]             = self.get('20s')
        self.info["label"]             = self.get('20s')
        self.info["date"]              = self.get('10s')
        self.info["time"]              = self.get('12s')
        self.info["mean_age"]          = self.get('f')
        self.info["stdev"]             = self.get('f')
        self.info["n"]                 = self.get('h')
        self.info["compfile"]          = self.get('38s')
        self.info["spectwincomp"]      = self.get('f')
        self.info["meanaccuracy"]      = self.get('f')
        self.info["meanlatency"]       = self.get('f')
        self.info["sortfile"]          = self.get('46s')
        self.info["numevents"]         = self.get('i')
        self.info["compoper"]          = self.get('b')
        self.info["avgmode"]           = self.get('b')
        self.info["review"]            = self.get('b')
        self.info["nsweeps"]           = self.get('H')
        self.info["compsweeps"]        = self.get('H')
        self.info["acceptcnt"]         = self.get('H')
        self.info["rejectcnt"]         = self.get('H')
        self.info["pnts"]              = self.get('H')
        self.info["nchannels"]         = self.get('H')
        self.info["avgupdate"]         = self.get('H')
        self.info["domain"]            = self.get('b')
        self.info["variance"]          = self.get('b')
        self.info["rate"]              = self.get('H')
        self.info["scale"]             = self.get('d')
        self.info["veogcorrect"]       = self.get('b')
        self.info["heogcorrect"]       = self.get('b')
        self.info["aux1correct"]       = self.get('b')
        self.info["aux2correct"]       = self.get('b')
        self.info["veogtrig"]          = self.get('f')
        self.info["heogtrig"]          = self.get('f')
        self.info["aux1trig"]          = self.get('f')
        self.info["aux2trig"]          = self.get('f')
        self.info["heogchnl"]          = self.get('h')
        self.info["veogchnl"]          = self.get('h')
        self.info["aux1chnl"]          = self.get('h')
        self.info["aux2chnl"]          = self.get('h')
        self.info["veogdir"]           = self.get('b')
        self.info["heogdir"]           = self.get('b')
        self.info["aux1dir"]           = self.get('b')
        self.info["aux2dir"]           = self.get('b')
        self.info["veog_n"]            = self.get('h')
        self.info["heog_n"]            = self.get('h')
        self.info["aux1_n"]            = self.get('h')
        self.info["aux2_n"]            = self.get('h')
        self.info["veogmaxcnt"]        = self.get('h')
        self.info["heogmaxcnt"]        = self.get('h')
        self.info["aux1maxcnt"]        = self.get('h')
        self.info["aux2maxcnt"]        = self.get('h')
        self.info["veogmethod"]        = self.get('b')
        self.info["heogmethod"]        = self.get('b')
        self.info["aux1method"]        = self.get('b')
        self.info["aux2method"]        = self.get('b')
        self.info["ampsensitivity"]    = self.get('f')
        self.info["lowpass"]           = self.get('b')
        self.info["highpass"]          = self.get('b')
        self.info["notch"]             = self.get('b')
        self.info["autoclipadd"]       = self.get('b')
        self.info["baseline"]          = self.get('b')
        self.info["offstart"]          = self.get('f')
        self.info["offstop"]           = self.get('f')
        self.info["reject"]            = self.get('b')
        self.info["rejstart"]          = self.get('f')
        self.info["rejstop"]           = self.get('f')
        self.info["rejmin"]            = self.get('f')
        self.info["rejmax"]            = self.get('f')
        self.info["trigtype"]          = self.get('b')
        self.info["trigval"]           = self.get('f')
        self.info["trigchnl"]          = self.get('b')
        self.info["trigmask"]          = self.get('h')
        self.info["trigisi"]           = self.get('f')
        self.info["trigmin"]           = self.get('f')
        self.info["trigmax"]           = self.get('f')
        self.info["trigdir"]           = self.get('b')
        self.info["autoscale"]         = self.get('b')
        self.info["n2"]                = self.get('h')
        self.info["dir"]               = self.get('b')
        self.info["dispmin"]           = self.get('f')
        self.info["dispmax"]           = self.get('f')
        self.info["xmin"]              = self.get('f')
        self.info["xmax"]              = self.get('f')
        self.info["automin"]           = self.get('f')
        self.info["automax"]           = self.get('f')
        self.info["zmin"]              = self.get('f')
        self.info["zmax"]              = self.get('f')
        self.info["lowcut"]            = self.get('f')
        self.info["highcut"]           = self.get('f')
        self.info["common"]            = self.get('b')
        self.info["savemode"]          = self.get('b')
        self.info["manmode"]           = self.get('b')
        self.info["ref"]               = self.get('10s')
        self.info["rectify"]           = self.get('b')
        self.info["displayxmin"]       = self.get('f')
        self.info["displayxmax"]       = self.get('f')
        self.info["phase"]             = self.get('b')
        self.info["screen"]            = self.get('16s')
        self.info["calmode"]           = self.get('h')
        self.info["calmethod"]         = self.get('h')
        self.info["calupdate"]         = self.get('h')
        self.info["calbaseline"]       = self.get('h')
        self.info["calsweeps"]         = self.get('h')
        self.info["calattenuator"]     = self.get('f')
        self.info["calpulsevolt"]      = self.get('f')
        self.info["calpulsestart"]     = self.get('f')
        self.info["calpulsestop"]      = self.get('f')
        self.info["calfreq"]           = self.get('f')
        self.info["taskfile"]          = self.get('34s')
        self.info["seqfile"]           = self.get('34s')
        self.info["spectmethod"]       = self.get('b')
        self.info["spectscaling"]      = self.get('b')
        self.info["spectwindow"]       = self.get('b')
        self.info["spectwinlength"]    = self.get('f')
        self.info["spectorder"]        = self.get('b')
        self.info["notchfilter"]       = self.get('b')
        self.info["headgain"]          = self.get('h')
        self.info["additionalfiles"]   = self.get('i')
        self.info["unused"]            = self.get('5s')
        self.info["fspstopmethod"]     = self.get('h')
        self.info["fspstopmode"]       = self.get('h')
        self.info["fspfvalue"]         = self.get('f')
        self.info["fsppoint"]          = self.get('h')
        self.info["fspblocksize"]      = self.get('h')
        self.info["fspp1"]             = self.get('H')
        self.info["fspp2"]             = self.get('H')
        self.info["fspalpha"]          = self.get('f')
        self.info["fspnoise"]          = self.get('f')
        self.info["fspv1"]             = self.get('h')
        self.info["montage"]           = self.get('40s')
        self.info["eventfile"]         = self.get('40s')
        self.info["fratio"]            = self.get('f')
        self.info["minor_rev"]         = self.get('b')
        self.info["eegupdate"]         = self.get('h')
        self.info["compressed"]        = self.get('b')
        self.info["xscale"]            = self.get('f')
        self.info["yscale"]            = self.get('f')
        self.info["xsize"]             = self.get('f')
        self.info["ysize"]             = self.get('f')
        self.info["acmode"]            = self.get('b')
        self.info["commonchnl"]        = self.get('B')
        self.info["xtics"]             = self.get('b')
        self.info["xrange"]            = self.get('b')
        self.info["ytics"]             = self.get('b')
        self.info["yrange"]            = self.get('b')
        self.info["xscalevalue"]       = self.get('f')
        self.info["xscaleinterval"]    = self.get('f')
        self.info["yscalevalue"]       = self.get('f')
        self.info["yscaleinterval"]    = self.get('f')
        self.info["scaletoolx1"]       = self.get('f')
        self.info["scaletooly1"]       = self.get('f')
        self.info["scaletoolx2"]       = self.get('f')
        self.info["scaletooly2"]       = self.get('f')
        self.info["port"]              = self.get('h')
        self.info["nsamples"]          = self.get('L')
        self.info["filterflag"]        = self.get('b')
        self.info["lowcutoff"]         = self.get('f')
        self.info["lowpoles"]          = self.get('h')
        self.info["highcutoff"]        = self.get('f')
        self.info["highpoles"]         = self.get('h')
        self.info["filtertype"]        = self.get('b')
        self.info["filterdomain"]      = self.get('b')
        self.info["snrflag"]           = self.get('b')
        self.info["coherenceflag"]     = self.get('b')
        self.info["continuoustype"]    = self.get('b')
        self.info["eventtablepos"]     = self.get('L')
        self.info["continuousseconds"] = self.get('f')
        self.info["channeloffset"]     = self.get('l')
        self.info["autocorrectflag"]   = self.get('b')
        self.info["dcthreshold"]       = self.get('B')
        
        # The value stored for nsamples is sometimes wrong, for some reason.
        # This code corrects it.
        
        begdata = 900 + (self.info["nchannels"] * 75)
        enddata = self.info["eventtablepos"]
        nsamples = ((enddata - begdata)/self.info["nchannels"])/2
        
        self.info["nsamples"]          = nsamples
    
    def get_channel(self, channel):
        print "Converting channel", channel, "(%s)" % self.electrodes[channel], "..." 
        
        nsamples  = self.info["nsamples"]
        nchannels = self.info["nchannels"]
        rate      = self.info["rate"]
        print nsamples, nchannels, rate #EFL
        
        numbytes = 2 # FIXME
        chan_offset = channel
        sample_offset = nchannels
        self.file.seek(900 + (nchannels * 75) + (chan_offset * numbytes))
        chunk = 'h' + str(numbytes * (nchannels - 1)) + 'x'
        divisor = int(rate)
        
        # Get data in chunks (or "blocks") of size nsamples/divisor, instead of all at once.
        data = zeros(nsamples, dtype='int16')
        for block in xrange((nsamples-1)/divisor):
            a = block * divisor            
            b = (block+1) * divisor
            data[a:b] = self.get(chunk * divisor)
        
        # Get the remainder that doesn't divide into divisor.
        remainder =  nsamples - b
        data[b:] = self.get(chunk * (remainder-1) + "h" + ((nchannels * numbytes - (2 * channel)) * "x"))
        
        # Convert int into float
        baseline    = self.electrodes[channel].baseline
        sensitivity = self.electrodes[channel].sensitivity
        scale       = self.electrodes[channel].calib
        
        data = (data - baseline) * ((sensitivity * scale) / 204.8)
        
        return data
    
    def save_continuous_data(self):
        """Get continuous data from cnt file and store it in a CArray in an HDF5 file."""
                
        nsamples  = self.info["nsamples"]
        nchannels = self.info["nchannels"]
        
        shape = (nsamples, nchannels)
        atom  = tables.Float32Atom()
        filters = tables.Filters(complevel=0)
        ca = self.h5.createCArray(self.h5.root, 'data', atom, shape, title="Continuous Data", filters=filters)
        
        self.file.seek(900 + (75 * nchannels))
        for channel in xrange(nchannels):
            ca[:, channel] = self.get_channel(channel)
            
    def save_data(self):
        self.create_h5()
        
        self.save_continuous_data()
        self.save_events()
                
        self.h5.close()
        
    def get_event_table(self):
        event_offset = self.info["eventtablepos"]
        self.file.seek(event_offset)
        
        self.event_table = {}
        self.event_table["teeg"]   = self.get('B')
        self.event_table["size"]   = self.get('L')
        self.event_table["offset"] = self.get('L')
    
    def get_event(self):
        """Read a Type 2 event."""
        
        event = Event()
        event.stimtype   = self.get('H')
        event.keyboard   = self.get('c')
        event.temp       = self.get('B')
        event.offset     = self.convert_bytes_to_points(self.get('l'))
        event.etype      = self.get('h')
        event.code       = self.get('h')
        event.latency    = self.get('f')
        event.epochevent = self.get('c')
        event.accept     = self.get('c')
        event.accuracy   = self.get('c')
        
        return event
        
    def load_events(self):
                
        nevents = self.event_table["size"] / 19
        self.events = [self.get_event() for event in xrange(nevents)]
    
    def save_events(self):
        
        self.get_event_table()
        self.load_events()
        
        shape = (len(self.events), 2)
        atom  = tables.Int32Atom()  ##16Atom() EFL
        filters = tables.Filters(complevel=5, complib='zlib')
        
        ca = self.h5.createCArray(self.h5.root, 'triggers', atom, shape, title="Trigger Data", filters=filters)
        
        for i, event in enumerate(self.events):
            ca[i, :] = [event.stimtype, event.offset]
        
    def convert_bytes_to_points(self, byte):
        data_offset = 900 + (75 * self.info["nchannels"])
        point = (byte - data_offset) / (2 * self.info["nchannels"])
        
        return point
    
            
if __name__ == "__main__":
    
    for cnt_filename in sys.argv[1:]:
        if os.path.splitext(cnt_filename)[-1].lower() != ".cnt":
            try:
                raise ValueError("Input files should have a .cnt extension.")
            except ValueError:
                print "Input files should have a .cnt extension."
                sys.exit(0)
        else:
            print cnt_filename
            CNTData(cnt_filename)
    