# prototxt_basic
import sys
import pprint

attrstr = "attrs"

def data(txt_file, info):
  txt_file.write('name: "mxnet-mdoel"\n')
  txt_file.write('layer {\n')
  txt_file.write('  name: "data"\n')
  txt_file.write('  type: "Input"\n')
  txt_file.write('  top: "data"\n')
  txt_file.write('  input_param {\n')
  txt_file.write('    shape: { dim: 1 dim: 3 dim: 112 dim: 112 }\n') # TODO
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')

def fuzzy_haskey(d, key):
  for eachkey in d:
    if key in eachkey:
      return True
  return False
  
def Convolution(txt_file, info):
  #if info['attrs']['no_bias'] == 'True':
    #bias_term = 'false'
  #else:
    #bias_term = 'true'  
  #if info['top'] == 'conv1_1':
    #pprint.pprint(info)  
  # print('\n-------debug----------\n',info,'\n-------debug----------\n')
  if fuzzy_haskey(info['params'], 'bias'):
    bias_term = 'true'
  elif 'no_bias' in info[attrstr] and info['attrs']['no_bias'] == 'True':
    bias_term = 'false'
  else:
    bias_term = 'true'
  txt_file.write('layer {\n')
  txt_file.write('	bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('	top: "%s"\n'          % info['top'])
  txt_file.write('	name: "%s"\n'         % info['top'])
  txt_file.write('	type: "Convolution"\n')
  txt_file.write('	convolution_param {\n')
  attrstr_ = 'param'
  txt_file.write('		num_output: %s\n'   % info[attrstr_]['num_filter'])
  txt_file.write('		kernel_size: %s\n'  % info[attrstr_]['kernel'].split('(')[1].split(',')[0]) # TODO
  if 'pad' in info[attrstr_]:
    txt_file.write('		pad: %s\n'          % info[attrstr_]['pad'].split('(')[1].split(',')[0]) # TODO
  if 'num_group' in info[attrstr_]  and int(info[attrstr_]['num_group']) != 1:
    txt_file.write('		group: %s\n'        % info[attrstr_]['num_group'])
    txt_file.write('            engine:CAFFE\n')
  if 'stride' in info[attrstr_]:
    txt_file.write('		stride: %s\n'       % info[attrstr_]['stride'].split('(')[1].split(',')[0])
  txt_file.write('		bias_term: %s\n'    % bias_term)
  txt_file.write('	}\n')
  if 'share' in info.keys() and info['share']:  
    txt_file.write('	param {\n')
    txt_file.write('	  name: "%s"\n'     % info['params'][0])
    txt_file.write('	}\n')
  txt_file.write('}\n')
  txt_file.write('\n')  

def ChannelwiseConvolution(txt_file, info):
  Convolution(txt_file, info)
  
def BatchNorm(txt_file, info):
  #pprint.pprint(info)
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "BatchNorm"\n')
  txt_file.write('  batch_norm_param {\n')
  txt_file.write('    use_global_stats: true\n')        # TODO
  if 'momentum' in info[attrstr]:
    txt_file.write('    moving_average_fraction: %s\n' % info[attrstr]['momentum'])
  else:
    txt_file.write('    moving_average_fraction: 0.9\n')
  if 'eps' in info[attrstr]:
    txt_file.write('    eps: %s\n' % info[attrstr]['eps'])
  else:
    txt_file.write('    eps: 0.001\n')                   
  txt_file.write('  }\n')
  txt_file.write('}\n')
  # if info['fix_gamma']=="False":                    # TODO
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['top'])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s_scale"\n'   % info['top'])
  txt_file.write('  type: "Scale"\n')
  txt_file.write('  scale_param { bias_term: true }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Activation(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "ReLU"\n')      # TODO
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Concat(txt_file, info):
  # print('\n-------debug----------\n',info,'\n-------debug----------\n')
  attrstr_ = 'param'
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Concat"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  concat_param { \n axis: %s\n }\n'          % info[attrstr_]['dim'])
  txt_file.write('}\n')
  txt_file.write('\n')
  pass
  
def ElementWiseSum(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Eltwise"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  eltwise_param { operation: SUM }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Pooling(txt_file, info):
  attrstr_='param'
  # print('\n-------debug----------\n',info,'\n-------debug----------\n')
  pool_type = 'AVE' if info[attrstr_]['pool_type'] == 'avg' else 'MAX'
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Pooling"\n')
  txt_file.write('  pooling_param {\n')
  txt_file.write('    pool: %s\n'         % pool_type)       # TODO
  txt_file.write('    kernel_size: %s\n'  % info[attrstr_]['kernel'].split('(')[1].split(',')[0])
  #txt_file.write('    stride: %s\n'       % info[attrstr]['stride'].split('(')[1].split(',')[0])
  if 'pad' in info[attrstr_]:
    txt_file.write('    pad: %s\n'          % info[attrstr_]['pad'].split('(')[1].split(',')[0])
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def FullyConnected(txt_file, info):
  attrstr_='param'
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "InnerProduct"\n')
  txt_file.write('  inner_product_param {\n')
  txt_file.write('    num_output: %s\n' % info[attrstr_]['num_hidden'])
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Flatten(txt_file, info):
  pass
  
def Softmax(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "Softmax"\n')
  txt_file.write('}\n')
  txt_file.write('\n')

def LeakyReLU(txt_file, info):
  if info[attrstr]['act_type'] == 'elu':
    txt_file.write('layer {\n')
    txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
    txt_file.write('  top: "%s"\n'        % info['top'])
    txt_file.write('  name: "%s"\n'       % info['top'])
    txt_file.write('  type: "ELU"\n')
    txt_file.write('  elu_param { alpha: 0.25 }\n')
    txt_file.write('}\n')
    txt_file.write('\n')
  elif info[attrstr]['act_type'] == 'prelu':
    txt_file.write('layer {\n')
    txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
    txt_file.write('  top: "%s"\n'        % info['top'])
    txt_file.write('  name: "%s"\n'       % info['top'])
    txt_file.write('  type: "PReLU"\n')
    txt_file.write('}\n')
    txt_file.write('\n')      
  else:
    raise Exception("unsupported Activation")

def Eltwise(txt_file, info, op):
  txt_file.write('layer {\n')
  txt_file.write('  type: "Eltwise"\n')
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  for btom in info['bottom']:
      txt_file.write('  bottom: "%s"\n' % btom)
  txt_file.write('  eltwise_param { operation: %s }\n' % op)
  txt_file.write('}\n')
  txt_file.write('\n')  

# ----------------------------------------------------------------
def write_node(txt_file, info):
    if 'label' in info['name']:
        return        
    if info['op'] == 'null' and info['name'] == 'data':
        data(txt_file, info)
    elif info['op'] == 'Convolution':
        Convolution(txt_file, info)
    elif info['op'] == 'ChannelwiseConvolution':
        ChannelwiseConvolution(txt_file, info)
    elif info['op'] == 'BatchNorm':
        BatchNorm(txt_file, info)
    elif info['op'] == 'Activation':
        Activation(txt_file, info)
    elif info['op'] == 'ElementWiseSum':
        ElementWiseSum(txt_file, info)
    elif info['op'] == '_Plus':
        ElementWiseSum(txt_file, info)
    elif info['op'] == 'Concat':
        Concat(txt_file, info)
    elif info['op'] == 'Pooling':
        Pooling(txt_file, info)
    elif info['op'] == 'Flatten':
        Flatten(txt_file, info)
    elif info['op'] == 'FullyConnected':
        FullyConnected(txt_file, info)
    elif info['op'] == 'SoftmaxOutput':
        Softmax(txt_file, info)
    elif info['op'] == 'LeakyReLU':
        LeakyReLU(txt_file, info)
    elif info['op'] == 'elemwise_add':
        ElementWiseSum(txt_file, info)
    else:
        #pprint.pprint(info)
        #sys.exit("Warning!  Unknown mxnet op:{}".format(info['op']))
        print("Warning! Skip Unknown mxnet op:{}".format(info['op']))
