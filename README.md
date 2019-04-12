## ForceFeeder 

Force activated LED stimulus assay. Forces produced by fruits are detected
using a micro force Sensor, e.g. by touching a beam. Forces above the user
specified threshold trigger a light (fake food) stimulus.   


## Installation

Requirements: python-serial, python-numpy, python-matplotlib

```bash
$ python setup.py install 

```


## YAML Configuration Example 

``` yml

data_file: 'data.txt'

ports:
    loadcell: '/dev/loadcell'
    ledpwm:   '/dev/ledpwm'

window:
    size_t: 10.0
    size_f: 5.0 

stimulus:
    pin: 3
    on_value: 255 
    off_value: 0
    on_dt: 1.0
    off_dt: 0.0

threshold:
    value: 1.0
    window: 0.5

highpass_filter:
    enabled: False
    cutoff_freq: 0.05

```


## Command Line

```bash
$ force_feeder config.yaml

```
