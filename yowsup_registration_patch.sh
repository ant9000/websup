#!/bin/bash

(
cat<<PATCH
--- env/lib/python2.7/site-packages/yowsup/registration/coderequest.py.dist 2015-02-12 19:00:52.692421332 +0100
+++ env/lib/python2.7/site-packages/yowsup/registration/coderequest.py  2015-02-12 18:02:32.031039253 +0100
@@ -20,14 +20,14 @@
         self.addParam("in", p_in)
         self.addParam("lc", "GB")
         self.addParam("lg", "en")
-        self.addParam("mcc", "000")
-        self.addParam("mnc", "000")
+#       self.addParam("mcc", "000")
+#       self.addParam("mnc", "000")
         self.addParam("sim_mcc", sim_mcc.zfill(3))
         self.addParam("sim_mnc", sim_mnc.zfill(3))
         self.addParam("method", method)
         #self.addParam("id", idx)
-        self.addParam("network_radio_type", "1")
-        self.addParam("reason", "self-send-jailbroken")
+#       self.addParam("network_radio_type", "1")
+#       self.addParam("reason", "self-send-jailbroken")
 
 
         self.addParam("token", CURRENT_ENV.getToken(p_in))
PATCH
)|patch -p0

