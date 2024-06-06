# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: param.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bparam.proto\x12\x07\x65xample\"4\n\x06Tensor\x12\x0c\n\x04node\x18\x01 \x01(\t\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\r\n\x05shape\x18\x03 \x03(\x05\"k\n\x0bVectorParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.example.Tensor\x12\x1e\n\x05other\x18\x04 \x01(\x0b\x32\x0f.example.Tensor\"\xd2\x01\n\x0bMatrixParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.example.Tensor\x12\x1f\n\x06weight\x18\x04 \x01(\x0b\x32\x0f.example.Tensor\x12\x1d\n\x04\x62ias\x18\x05 \x01(\x0b\x32\x0f.example.Tensor\x12\x0e\n\x06stride\x18\x06 \x03(\x05\x12\x0f\n\x07padding\x18\x07 \x03(\x05\x12\x10\n\x08\x64ilation\x18\x08 \x03(\x05\x12\x12\n\ntransposed\x18\t \x01(\x08\"\xf1\x01\n\x0cPoolingParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.example.Tensor\x12\x13\n\x0bkernel_size\x18\x04 \x03(\x05\x12\x0e\n\x06stride\x18\x05 \x03(\x05\x12\x0f\n\x07padding\x18\x06 \x03(\x05\x12\x10\n\x08\x64ilation\x18\x07 \x03(\x05\x12\x11\n\tceil_mode\x18\x08 \x01(\x08\x12\x19\n\x11\x63ount_include_pad\x18\t \x01(\x08\x12\x18\n\x10\x64ivisor_override\x18\n \x01(\x05\x12\x13\n\x0boutput_size\x18\x0b \x03(\x05\"i\n\x0bReduceParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.example.Tensor\x12\x0b\n\x03\x64im\x18\x04 \x03(\x05\x12\x0f\n\x07keepdim\x18\x05 \x01(\x08\"X\n\nShapeParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06opcode\x18\x02 \x01(\t\x12\x1e\n\x05input\x18\x03 \x01(\x0b\x32\x0f.example.Tensor\x12\x0c\n\x04\x64ims\x18\x04 \x03(\x05\"\x93\x02\n\x10\x41\x63\x63\x65leratorParam\x12\x0c\n\x04name\x18\x01 \x01(\t\x12,\n\x0cmatrix_param\x18\x02 \x01(\x0b\x32\x14.example.MatrixParamH\x00\x12.\n\rpooling_param\x18\x03 \x01(\x0b\x32\x15.example.PoolingParamH\x00\x12,\n\x0creduce_param\x18\x04 \x01(\x0b\x32\x14.example.ReduceParamH\x00\x12*\n\x0bshape_param\x18\x05 \x01(\x0b\x32\x13.example.ShapeParamH\x00\x12+\n\rvector_params\x18\x06 \x03(\x0b\x32\x14.example.VectorParamB\x0c\n\nparam_type\"8\n\x0bModelParams\x12)\n\x06params\x18\x01 \x03(\x0b\x32\x19.example.AcceleratorParamb\x06proto3')



_TENSOR = DESCRIPTOR.message_types_by_name['Tensor']
_VECTORPARAM = DESCRIPTOR.message_types_by_name['VectorParam']
_MATRIXPARAM = DESCRIPTOR.message_types_by_name['MatrixParam']
_POOLINGPARAM = DESCRIPTOR.message_types_by_name['PoolingParam']
_REDUCEPARAM = DESCRIPTOR.message_types_by_name['ReduceParam']
_SHAPEPARAM = DESCRIPTOR.message_types_by_name['ShapeParam']
_ACCELERATORPARAM = DESCRIPTOR.message_types_by_name['AcceleratorParam']
_MODELPARAMS = DESCRIPTOR.message_types_by_name['ModelParams']
Tensor = _reflection.GeneratedProtocolMessageType('Tensor', (_message.Message,), {
  'DESCRIPTOR' : _TENSOR,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.Tensor)
  })
_sym_db.RegisterMessage(Tensor)

VectorParam = _reflection.GeneratedProtocolMessageType('VectorParam', (_message.Message,), {
  'DESCRIPTOR' : _VECTORPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.VectorParam)
  })
_sym_db.RegisterMessage(VectorParam)

MatrixParam = _reflection.GeneratedProtocolMessageType('MatrixParam', (_message.Message,), {
  'DESCRIPTOR' : _MATRIXPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.MatrixParam)
  })
_sym_db.RegisterMessage(MatrixParam)

PoolingParam = _reflection.GeneratedProtocolMessageType('PoolingParam', (_message.Message,), {
  'DESCRIPTOR' : _POOLINGPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.PoolingParam)
  })
_sym_db.RegisterMessage(PoolingParam)

ReduceParam = _reflection.GeneratedProtocolMessageType('ReduceParam', (_message.Message,), {
  'DESCRIPTOR' : _REDUCEPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.ReduceParam)
  })
_sym_db.RegisterMessage(ReduceParam)

ShapeParam = _reflection.GeneratedProtocolMessageType('ShapeParam', (_message.Message,), {
  'DESCRIPTOR' : _SHAPEPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.ShapeParam)
  })
_sym_db.RegisterMessage(ShapeParam)

AcceleratorParam = _reflection.GeneratedProtocolMessageType('AcceleratorParam', (_message.Message,), {
  'DESCRIPTOR' : _ACCELERATORPARAM,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.AcceleratorParam)
  })
_sym_db.RegisterMessage(AcceleratorParam)

ModelParams = _reflection.GeneratedProtocolMessageType('ModelParams', (_message.Message,), {
  'DESCRIPTOR' : _MODELPARAMS,
  '__module__' : 'param_pb2'
  # @@protoc_insertion_point(class_scope:example.ModelParams)
  })
_sym_db.RegisterMessage(ModelParams)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TENSOR._serialized_start=24
  _TENSOR._serialized_end=76
  _VECTORPARAM._serialized_start=78
  _VECTORPARAM._serialized_end=185
  _MATRIXPARAM._serialized_start=188
  _MATRIXPARAM._serialized_end=398
  _POOLINGPARAM._serialized_start=401
  _POOLINGPARAM._serialized_end=642
  _REDUCEPARAM._serialized_start=644
  _REDUCEPARAM._serialized_end=749
  _SHAPEPARAM._serialized_start=751
  _SHAPEPARAM._serialized_end=839
  _ACCELERATORPARAM._serialized_start=842
  _ACCELERATORPARAM._serialized_end=1117
  _MODELPARAMS._serialized_start=1119
  _MODELPARAMS._serialized_end=1175
# @@protoc_insertion_point(module_scope)
