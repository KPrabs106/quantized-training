# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: param.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bparam.proto\x12\x07\x63odegen\"+\n\x06Memory\x12\x11\n\tpartition\x18\x01 \x01(\x05\x12\x0e\n\x06offset\x18\x02 \x01(\x05\"H\n\x0bPermutation\x12\x0c\n\x04node\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\r\n\x05shape\x18\x03 \x03(\x05\x12\x0c\n\x04\x64ims\x18\x04 \x03(\x05\"\x80\x01\n\x06Tensor\x12\x0c\n\x04node\x18\x01 \x01(\t\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\r\n\x05shape\x18\x03 \x03(\x05\x12\x1f\n\x06memory\x18\x04 \x01(\x0b\x32\x0f.codegen.Memory\x12)\n\x0bpermutation\x18\x05 \x01(\x0b\x32\x14.codegen.Permutation\"J\n\x08MXTensor\x12\x1e\n\x05input\x18\x01 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x1e\n\x05scale\x18\x02 \x01(\x0b\x32\x0f.codegen.Tensor\"k\n\x0bVectorParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x1e\n\x05other\x18\x04 \x01(\x0b\x32\x0f.codegen.Tensor\"\xbe\x02\n\x0bMatrixParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12 \n\x05input\x18\x03 \x01(\x0b\x32\x0f.codegen.TensorH\x00\x12%\n\x08mx_input\x18\n \x01(\x0b\x32\x11.codegen.MXTensorH\x00\x12!\n\x06weight\x18\x04 \x01(\x0b\x32\x0f.codegen.TensorH\x01\x12&\n\tmx_weight\x18\x0b \x01(\x0b\x32\x11.codegen.MXTensorH\x01\x12\x1d\n\x04\x62ias\x18\x05 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x0e\n\x06stride\x18\x06 \x03(\x05\x12\x0f\n\x07padding\x18\x07 \x03(\x05\x12\x10\n\x08\x64ilation\x18\x08 \x03(\x05\x12\x0e\n\x06groups\x18\t \x01(\x05\x42\x0c\n\ninput_typeB\r\n\x0bweight_type\"\xf1\x01\n\x0cPoolingParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x13\n\x0bkernel_size\x18\x04 \x03(\x05\x12\x0e\n\x06stride\x18\x05 \x03(\x05\x12\x0f\n\x07padding\x18\x06 \x03(\x05\x12\x10\n\x08\x64ilation\x18\x07 \x03(\x05\x12\x11\n\tceil_mode\x18\x08 \x01(\x08\x12\x19\n\x11\x63ount_include_pad\x18\t \x01(\x08\x12\x18\n\x10\x64ivisor_override\x18\n \x01(\x05\x12\x13\n\x0boutput_size\x18\x0b \x03(\x05\"i\n\x0bReduceParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x0b\n\x03\x64im\x18\x04 \x03(\x05\x12\x0f\n\x07keepdim\x18\x05 \x01(\x08\"Z\n\x0cReshapeParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.codegen.Tensor\x12\x0c\n\x04\x64ims\x18\x04 \x03(\x05\"\xb8\x02\n\x10\x41\x63\x63\x65leratorParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12,\n\x0cmatrix_param\x18\x02 \x01(\x0b\x32\x14.codegen.MatrixParamH\x00\x12.\n\rpooling_param\x18\x03 \x01(\x0b\x32\x15.codegen.PoolingParamH\x00\x12,\n\x0creduce_param\x18\x04 \x01(\x0b\x32\x14.codegen.ReduceParamH\x00\x12.\n\rreshape_param\x18\x05 \x01(\x0b\x32\x15.codegen.ReshapeParamH\x00\x12+\n\rvector_params\x18\x06 \x03(\x0b\x32\x14.codegen.VectorParam\x12\x1f\n\x06output\x18\x07 \x01(\x0b\x32\x0f.codegen.TensorB\x0c\n\nparam_type\"8\n\x0bModelParams\x12)\n\x06params\x18\x01 \x03(\x0b\x32\x19.codegen.AcceleratorParamb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'param_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MEMORY']._serialized_start=24
  _globals['_MEMORY']._serialized_end=67
  _globals['_PERMUTATION']._serialized_start=69
  _globals['_PERMUTATION']._serialized_end=141
  _globals['_TENSOR']._serialized_start=144
  _globals['_TENSOR']._serialized_end=272
  _globals['_MXTENSOR']._serialized_start=274
  _globals['_MXTENSOR']._serialized_end=348
  _globals['_VECTORPARAM']._serialized_start=350
  _globals['_VECTORPARAM']._serialized_end=457
  _globals['_MATRIXPARAM']._serialized_start=460
  _globals['_MATRIXPARAM']._serialized_end=778
  _globals['_POOLINGPARAM']._serialized_start=781
  _globals['_POOLINGPARAM']._serialized_end=1022
  _globals['_REDUCEPARAM']._serialized_start=1024
  _globals['_REDUCEPARAM']._serialized_end=1129
  _globals['_RESHAPEPARAM']._serialized_start=1131
  _globals['_RESHAPEPARAM']._serialized_end=1221
  _globals['_ACCELERATORPARAM']._serialized_start=1224
  _globals['_ACCELERATORPARAM']._serialized_end=1536
  _globals['_MODELPARAMS']._serialized_start=1538
  _globals['_MODELPARAMS']._serialized_end=1594
# @@protoc_insertion_point(module_scope)
