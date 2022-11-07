# Subtracts the two emg signals and filters and saves the results.

# Import stuff
import numpy as np
from scipy.signal import butter, filtfilt, freqz
import easygui
import os
import sys
from tqdm import tqdm

# Get name of directory with the data files
if len(sys.argv) > 1:
    dir_name = os.path.abspath(sys.argv[1])
    if dir_name[-1] != '/':
        dir_name += '/'
else:
    dir_name = easygui.diropenbox(msg = 'Please select data directory')

os.chdir(dir_name)

# Load the data
emg_data = np.load('emg_data.npy')

# Ask the user for stimulus delivery time in each trial, and convert to an integer
pre_stim = easygui.multenterbox(
        msg = 'Enter the pre-stimulus time included in each trial', 
        fields = ['Pre-stimulus time (ms)']) 
pre_stim = int(pre_stim[0])

# Get coefficients for Butterworth filters
m, n = butter(2, 2.0*300.0/1000.0, 'highpass')
c, d = butter(2, 2.0*15.0/1000.0, 'lowpass')

#high_freq = 2.0*300.0/1000
#low_freq = 2.0*15.0/1000
#filt_order = 2
#fs = 1000
#m, n = butter(filt_order, high_freq, 'highpass')#, fs = fs)
#c, d = butter(filt_order, low_freq, 'lowpass')#, fs = fs)

# check how many EMG channels used in this experiment
check = easygui.ynbox(
        msg = 'Did you have more than one EMG channel?', 
        title = 'Check YES if you did')

# Bandpass filter the emg signals, and store them in a numpy array. 
# Low pass filter the bandpassed signals, and store them in another array
# Do not subtract channels at this stage...allow it as an option for future processing.
iters = list(np.ndindex(emg_data.shape[:-1])) 
emg_filt = np.zeros(emg_data.shape)
env = np.zeros(emg_data.shape)
for this_iter in tqdm(iters):
    temp_filt = filtfilt(m, n, emg_data[this_iter])
    emg_filt[this_iter] = temp_filt 
    env[this_iter] = filtfilt(c, d, np.abs(temp_filt))

#for i in range(emg_data.shape[1]):
#    for j in range(emg_data.shape[2]):
#        if check:
#            emg_filt[i, j, :] = \
#                    filtfilt(m, n, emg_data[0, i, j, :] - emg_data[1, i, j, :])
#        else:
#            emg_filt[i, j, :] = filtfilt(m, n, emg_data[0, i, j, :])
#        env[i, j, :] = filtfilt(c, d, np.abs(emg_filt[i, j, :]))    

## Get mean and std of baseline emg activity, 
## and use it to select trials that have significant post stimulus activity
sig_trials = np.zeros((emg_data.shape[1], emg_data.shape[2]))
pre_m = np.mean(np.abs(emg_filt[...,:pre_stim]), axis = (3))
pre_s = np.std(np.abs(emg_filt[...,:pre_stim]), axis = (3))

post_m = np.mean(np.abs(emg_filt[...,pre_stim:]), axis = (3))
post_max = np.max(np.abs(emg_filt[...,pre_stim:]), axis = (3))

# If any of the channels passes the criteria, select that trial as significant
mean_bool = np.sum(post_m > pre_m, axis = 0) > 0
std_bool = np.sum(post_max > (pre_m + 4.0*pre_s), axis = 0) > 0

# Logical AND
sig_trials = mean_bool * std_bool

#m = np.mean(np.abs(emg_filt[:, :, :pre_stim]))
#s = np.std(np.abs(emg_filt[:, :, :pre_stim]))
#for i in range(emg_data.shape[1]):
#    for j in range(emg_data.shape[2]):
#        if np.mean(np.abs(emg_filt[i, j, pre_stim:])) > m \
#                and np.max(np.abs(emg_filt[i, j, pre_stim:])) > m + 4.0*s:
#            sig_trials[i, j] = 1

# Save the highpass filtered signal, 
# the envelope and the indicator of significant trials as a np array
np.save('emg_filt.npy', emg_filt)
np.save('env.npy', env)
np.save('sig_trials.npy', sig_trials)
