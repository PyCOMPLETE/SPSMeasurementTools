import os
import gzip

def save_zip(out_complete_path):

	f_in = open(out_complete_path+'.mat', 'rb')
	f_out = gzip.open(out_complete_path+'.mat.gz', 'wb')
	f_out.writelines(f_in)
	f_out.close()
	f_in.close()
	os.remove(out_complete_path+'.mat')
	return
