#!/usr/bin/env python
#-*- coding:utf-8 -*-

def natbool(s):
	if s.lower() in ["y", "yes", "1", "true"]:
		return True
	elif s.lower() in ["n", "no", "0", "false"]:
		return False
	else:
		raise ValueError("Cannot convert %s to boolean" % s)
