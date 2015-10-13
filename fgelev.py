#!/usr/bin/env python2
import os
import logging
import cPickle
import subprocess
import calc_tile
import sys
from vec2d import vec2d


logger = logging.getLogger('fgelev')
#logger.setLevel("DEBUG")

class Probe_fgelev(object):
    """A drop-in replacement for Interpolator. Probes elevation via fgelev.
       Make sure to use the patched version of fgelev (see osm2city/fgelev/) or
       performance is likely to be terrible.

       By default, queries are cached. Call save_cache() to
       save the cache to disk before freeing the object.
    """
    def __init__(self, path_to_fgelev, path_to_scenery, fake=False, cache=True, auto_save_every=50000):
        """Open pipe to fgelev.
           Unless disabled by cache=False, initialize the cache and try to read
           it from disk. Automatically save the cache to disk every auto_save_every misses.
           If fake=True, never do any probing and return 0 on all queries.
        """
        self.fake = fake
        self.path_to_fgelev = path_to_fgelev
        self.PATH_TO_SCENERY = path_to_scenery
        self.auto_save_every = auto_save_every
        self.h_offset = 0
        self.fgelev_pipe = None
            
        if cache:
            self.pkl_fname = 'elev.pkl'
            try:
                logger.info("Loading %s", self.pkl_fname)
                fpickle = open(self.pkl_fname, 'rb')
                self._cache = cPickle.load(fpickle)
                fpickle.close()
                logger.info("OK")
            except IOError, reason:
                logger.warn("Loading elev cache failed (%s)", reason)
                self._cache = {}
        else:
            self._cache = None

    def open_fgelev(self):
        logger.info("Spawning fgelev")
        fg_root = "$FG_ROOT"
        self.fgelev_pipe = subprocess.Popen(self.path_to_fgelev + ' --expire 1000000 --fg-root ' + fg_root + ' --fg-scenery '+ self.PATH_TO_SCENERY, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # -- This should catch spawn errors, but it doesn't. We 
        #    check for sane return values on fgelev calls later.
#        if self.fgelev_pipe.poll() != 0:
#            raise RuntimeError("Spawning fgelev failed.")

    def save_cache(self):
        "save cache to disk"
        fpickle = open(self.pkl_fname, 'wb')
        cPickle.dump(self._cache, fpickle, -1)
        fpickle.close()

    def shift(self, h):
        self.h_offset += h

    def __call__(self, position, check_btg=False):
        """return elevation at (x,y). We try our cache first. Failing that,
           call fgelev.
        """
        def really_probe(position):
            if check_btg:
                btg_file = self.PATH_TO_SCENERY + os.sep + "Terrain" \
                           + os.sep + calc_tile.directory_name(position) + os.sep \
                           + calc_tile.construct_btg_file_name(position)
                print calc_tile.construct_btg_file_name(position)
                if not os.path.exists(btg_file):
                    logger.error("Terrain File " + btg_file + " does not exist. Set scenery path correctly or fly there with TerraSync enabled")
                    sys.exit(2)

            if not self.fgelev_pipe:
                self.open_fgelev()
            try:
                self.fgelev_pipe.stdin.write("%i %g %g\n" % (0, position.lon, position.lat))
            except IOError, reason:
                logger.error(reason)
 
            try:
                line = self.fgelev_pipe.stdout.readline()
                elev = float(line.split()[1]) + self.h_offset
            except IndexError, reason:
                logger.fatal("fgelev returned <%s>, resulting in %s. Did fgelev start OK?", line, reason)
                raise RuntimeError("fgelev errors are fatal.")

            return elev

        if self.fake:
            return 0.

        position = vec2d(position[0], position[1])

        if self._cache == None:
            return really_probe(position)

        key = (position.lon, position.lat)
        try:
            elev = self._cache[key]
            # logger.debug("hit %s %g" % (str(key), elev))
            return elev
        except KeyError:
            #logger.debug("miss (%i) %s" % (len(self._cache), str(key)))
            elev = really_probe(position)
            #logger.debug("   %g" % elev)
            self._cache[key] = elev

            if self.auto_save_every and len(self._cache) % self.auto_save_every == 0:
                self.save_cache()
            return elev
