# -*- coding: utf-8 -*-
"""DatasetModificado_MMdetecion_v.2.0

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11NSE1JmgH16gF6kjoc8SSyIb8vYwq29f

# Instalando a biblioteca MMDetection
> Selecione no menu `Ambiente de Execução` -> `Alterar o tipo de ambiente de execução` - > no campo `Acelerador de hardware ` escolha `GPU`.

> A biblioteca MMdetection contém diversos algoritmos de detecção de objetos implementados.

> Execute a célula abaixo clicando no símbolo do play para instalar. `demora um pouco :)`
"""



# Commented out IPython magic to ensure Python compatibility.
import os
from os.path import exists, join, basename, splitext

# %cd /content
git_repo_url = 'https://github.com/open-mmlab/mmdetection.git'
project_name = splitext(basename(git_repo_url))[0]
if not exists(project_name):
  !pip install dicttoxml
  !git clone $git_repo_url
  !pip install -q mmcv-full albumentations #mmcv==0.2.10 albumentations==0.3.2
  !pip install -q terminaltables imagecorruptions 
  !pip install -r {os.path.join(project_name, "requirements.txt")}
  !cd {project_name} && python setup.py develop
import sys
sys.path.append(project_name)

"""## Reinicie o ambiente após a instalação

> Selecione o menu `Ambiente de execução` -> `Reiniciar ambiente de execução` ou (ctrl+M) e escolha a opção `Sim`.

> Em seguida, execute a célula abaixo clicando no símbolo do play.
"""

#RESTART RUNTIME

# Check Pytorch installation
import torch, torchvision
print(torch.__version__, torch.cuda.is_available())

# Check MMDetection installation
import mmdet
print(mmdet.__version__)

import pycocotools
#print('Pycoco:',pycocotools.__version__)

# Check mmcv installation
from mmcv.ops import get_compiling_cuda_version, get_compiler_version
print(get_compiling_cuda_version())
print(get_compiler_version())
import mmcv
print(mmcv.__version__)

"""# Acessando o Google Drive para obter acessar as imagens

> Na célula abaixo, vamos executar os comandos para conectar o Colab com o Drive para acessar o diretório contendo as imagens.

> Ao clicar para executar, irá aparecer um `link` (exemplo: Go to this URL in a browser: https://accounts.google.com/...) para permitir o acesso ao seu Drive. 

Clique nesse link.

E na nova janela em que aparece `Escolha uma conta
para prosseguir para Google Drive File Stream` selecione a sua mesma conta do google Colab.

Faça o login (se precisar) e clique em `Permitir` (O app Google Drive File Stream quer acessar sua Conta do Google). 

Copie o código gerado (exemplo 4/1Ay0...) e cole no campo abaixo `Enter your authorization code:`

Pronto! Seu drive está conectado ao colab e irá aparecer do lado esquerdo a pasta `drive`.
"""

from google.colab import drive
drive.mount('/content/drive')

"""# Definindo as configurações do modelo a ser utilizando

> No exemplo abaixo temos 3 algoritmos de detecção `atss`, `sabl_cascade` e `vfnet`.

>Execute a célula abaixo
"""

#!wget http://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_x101_64x4d_fpn_1x_coco/faster_rcnn_x101_64x4d_fpn_1x_coco_20200204-833ee192.pth
!wget https://download.openmmlab.com/mmdetection/v2.0/atss/atss_r101_fpn_1x_coco/atss_r101_fpn_1x_20200825-dfcadd6f.pth
#!wget http://download.openmmlab.com/mmdetection/v2.0/paa/paa_r50_fpn_2x_coco/paa_r50_fpn_2x_coco_20200821-c98bfc4e.pth

#ADD MODELS
from mmcv import Config
import os
import sys
import time
import matplotlib
import matplotlib.pylab as plt
plt.rcParams["axes.grid"] = False

# You can add more model configs like below.
MODELS_CONFIG = {
    # METODOS NOVOS
    'faster_rcnn': {
        'config_file': 'configs/faster_rcnn/faster_rcnn_x101_64x4d_fpn_1x_coco.py',
        'checkpoint' : '/content/faster_rcnn_x101_64x4d_fpn_1x_coco_20200204-833ee192.pth'
    },
    'vfnet_r50': {
        'config_file': 'configs/vfnet/vfnet_r50_fpn_1x_coco.py',
        'checkpoint' : '/content/vfnet_r50_fpn_1x_coco_20201027-38db6f58.pth'
    },
    'sabl_r50':{
        'config_file': 'configs/sabl/sabl_cascade_rcnn_r50_fpn_1x_coco.py',
        'checkpoint' : '/content/drive/MyDrive/TrabalhoSAD/checkpoint/sabl_cascade_rcnn_r50_fpn_1x_coco-e1748e5e.pth'
    },
    'paa_r50':{
        'config_file': 'configs/paa/paa_r50_fpn_2x_coco.py',
        'checkpoint' : '/content/paa_r50_fpn_2x_coco_20200821-c98bfc4e.pth'
    },
    'detr_r50':{
        'config_file': 'configs/detr/detr_r50_8x2_150e_coco.py',
        'checkpoint' : '/content/detr_r50_8x2_150e_coco_20201130_194835-2c4b8974.pth'
    },
    'atss_r50':{
        'config_file': 'configs/atss/atss_r101_fpn_1x_coco.py',
        'checkpoint' : '/content/atss_r101_fpn_1x_20200825-dfcadd6f.pth'
    } 
}

def setCFG(selected_model,data_root,classes,total_epochs=12,learning_rate=0.01,size_bbox=15,fold='fold_1'): #TROCAR NUM DE EPOCHS

  # Pick the model you want to use
  # Select a model in `MODELS_CONFIG`.

  # Name of the config file.
  config_file = os.path.join('/content/mmdetection',MODELS_CONFIG[selected_model]['config_file'])

  from mmdet.apis import set_random_seed
  print(config_file)
  cfg = Config.fromfile(config_file)

  #resolver erro de epoch
  cfg.runner.max_epochs = total_epochs

  # Modify dataset type and path
  cfg.data_root = data_root#
  cfg.classes = classes  

  size_bbox = str(size_bbox)
  #defining configuration for test dataset
  cfg.data.test.type = cfg.dataset_type
  cfg.data.test.data_root = cfg.data_root
  cfg.data.test.ann_file = '/content/drive/MyDrive/IC/dataset/teste/test'
  cfg.data.test.classes = cfg.classes
  cfg.data.test.img_prefix = '/content/drive/MyDrive/IC/dataset/teste/img_rgb'

  #defining configuration for train dataset
  cfg.data.train.type = cfg.dataset_type
  cfg.data.train.data_root = cfg.data_root
  cfg.data.train.ann_file = '/content/drive/MyDrive/IC/dataset/train/train'
  cfg.data.train.classes = cfg.classes
  cfg.data.train.img_prefix = '/content/drive/MyDrive/IC/dataset/train/img_rgb'

  #defining configuration for val dataset
  cfg.data.val.type = cfg.dataset_type
  cfg.data.val.data_root = cfg.data_root
  cfg.data.val.ann_file = '/content/drive/MyDrive/IC/dataset/val/validation'
  cfg.data.val.classes = cfg.classes
  cfg.data.val.img_prefix =  '/content/drive/MyDrive/IC/dataset/val/img_rgb'
  cfg.data.val.pipeline = cfg.data.train.pipeline

  # modify num classes of the model in box head
  if 'roi_head' in cfg.model:
    #cfg.test_cfg.rcnn['score_thr']= 0.51
    if not isinstance(cfg.model.roi_head.bbox_head,list):
      cfg.model.roi_head.bbox_head['num_classes'] = len(cfg.classes)
    else: 
      for i in range(len(cfg.model.roi_head.bbox_head)):
        cfg.model.roi_head.bbox_head[i]['num_classes'] = len(cfg.classes)
  else:
      cfg.model.bbox_head['num_classes'] = len(cfg.classes)
      print(cfg.model.bbox_head['num_classes'],len(cfg.model.bbox_head))

  # We can still use the pre-trained Mask RCNN model though we do not need to
  # use the mask branch
  cfg.load_from =  MODELS_CONFIG[selected_model]['checkpoint']

  # Set up working dir to save files and logs.
  #cfg.work_dir = os.path.join(data_root,'MModels/'+'/%s'+ '/%s'%(selected_model, ))
  cfg.work_dir = os.path.join(data_root,'MModelsATSS_r101/'+'/%s'%(selected_model))
  print(cfg.work_dir)
  cfg.total_epochs = total_epochs

  # The original learning rate (LR) is set for 8-GPU training.
  # We divide it by 8 since we only use one GPU.
  cfg.optimizer.lr = learning_rate / 8
  #cfg.lr_config.warmup = None
  #cfg.log_config.interval = 100
  cfg.lr_config.policy = 'step'

  # Change the evaluation metric since we use customized dataset.
  cfg.evaluation.metric = 'bbox'
  # We can set the evaluation interval to reduce the evaluation times
  cfg.evaluation.interval = 1
  # We can set the checkpoint saving interval to reduce the storage cost
  cfg.checkpoint_config.interval = total_epochs/2
  cfg.checkpoint_config.create_symlink=True

  # Set seed thus the results are more reproducible
  cfg.seed = 0
  set_random_seed(0, deterministic=False)
  cfg.gpu_ids = range(1)


  # We can initialize the logger for training and have a look
  # at the final config used for training
  #print(f'Config:\n{cfg.pretty_text}')
  return cfg

"""#Teste do Dataset
> (OPCIONAL) Na célula abaixo, vamos conferir o conjunto de dados e os retangulos da anotação

"""

from mmdet.datasets import build_dataset,build_dataloader
from mmcv import Config
import mmcv
from mmcv.visualization import color_val
import cv2
import os
import torch
import numpy as np
#from mmdet.core import tensor2imgs
from mmcv.image import tensor2imgs
from mmdet.apis import set_random_seed
from google.colab.patches import cv2_imshow

selected_model='atss_r50' #MUDAR MODELO
cfg = setCFG(selected_model=selected_model,data_root='/content/drive/MyDrive/IC',classes=('boca de lobo',),total_epochs=12)

dataset = build_dataset(cfg.data.train, dict(test_mode=False,filter_empty_gt=False))
data_loader = build_dataloader(dataset,samples_per_gpu=1,workers_per_gpu=1,num_gpus=1,dist=False,shuffle=False)

img_norm_cfg = cfg.img_norm_cfg

for ims,data in enumerate(data_loader):
  if ims>10:
    break
  img_tensor = data['img'].data[0] 
  img_metas = data['img_metas'].data[0]
  print(img_metas[0]['filename'])
  
  result = data['gt_bboxes'].data[0] 
  
  colors = 'red' #muda a cor da retangulo ('blue', 'red', 'green','yellow')
  colors = [colors for _ in range(len(result))]
  colors = [color_val(c) for c in colors]  

  imgs = tensor2imgs(img_tensor, **img_norm_cfg)
  pos=0
  for img, img_meta in zip(imgs, img_metas):
    h, w, _ = img_meta['img_shape']
    img_show = img[:h, :w, :]
    print(ims,' img:')   
    bboxes = result[pos].numpy().astype(np.int32)
    for j in range(min(20, bboxes.shape[0])):
      left_top = (bboxes[j, 0], bboxes[j, 1])
      right_bottom = (bboxes[j, 2], bboxes[j, 3])
      cv2.rectangle(img_show, left_top, right_bottom, colors[pos], thickness=1)
    pos=pos+1
   
    cv2_imshow(img_show)

"""#Iniciando o treino do modelo

>Vamos então selecionar o modelo e iniciar o treino com o conjunto de treino e validação.

"""

from mmdet.datasets import build_dataset,build_dataloader
from mmdet.models import build_detector
from mmdet.apis import train_detector
from mmdet import __version__
from mmdet.utils import collect_env, get_root_logger
from mmcv.utils import get_git_hash
import torch
import os.path as osp

def trainModel(cfg):
  cfg.workflow = [('train', 1),('val', 1)]

  torch.backends.cudnn.benchmark = True
  distributed = False

  # Create work_dir
  print('Create workdir:',mmcv.mkdir_or_exist(osp.abspath(cfg.work_dir)))

  # dump config
  cfg.dump(osp.join(cfg.work_dir, osp.basename(selected_model+'.py')))
  # init the logger before other steps
  timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
  log_file = osp.join(cfg.work_dir, f'{timestamp}.log')
  logger = get_root_logger(log_file=log_file, log_level=cfg.log_level)

  # init the meta dict to record some important information such as
  # environment info and seed, which will be logged
  meta = dict()
  # log env info
  env_info_dict = collect_env()
  env_info = '\n'.join([(f'{k}: {v}') for k, v in env_info_dict.items()])
  dash_line = '-' * 60 + '\n'
  logger.info('Environment info:\n' + dash_line + env_info + '\n' +
              dash_line)
  meta['env_info'] = env_info
  meta['config'] = cfg.pretty_text
  # log some basic info
  logger.info(f'Distributed training: {distributed}')
  logger.info(f'Config:\n{cfg.pretty_text}')

  # set random seeds
  meta['seed'] = cfg.seed
  meta['exp_name'] = osp.basename(selected_model+'.py')


  # Build dataset
  datasets = [build_dataset(cfg.data.train,dict(test_mode=False,filter_empty_gt=False))]
  datasets.append(build_dataset(cfg.data.val,dict(test_mode=False,filter_empty_gt=False)))


  datasets[0].CLASSES = cfg.classes
  datasets[1].CLASSES = cfg.classes

  cfg.checkpoint_config.meta = dict(
              mmdet_version=__version__ + get_git_hash()[:7],
              CLASSES=datasets[0].CLASSES)

  # Build the detector
  #model = build_detector(
  #    cfg.model)
  model = build_detector(cfg.model,train_cfg=cfg.get('train_cfg'),test_cfg=cfg.get('test_cfg'))
  # Add an attribute for visualization convenience
  model.CLASSES = datasets[0].CLASSES

  train_detector(model, datasets, cfg, distributed=False, validate=False,timestamp=timestamp,meta=meta)

"""## Executando o treino E escolhendo o modelo
> Na célula abaixo estamos enviando as configurações para realizar o treino. 


1.   `selected_model`: o modelo selecionado
2.   `data_root`:  a pasta contendo todas as imagens
3.   `classes`: lista com o nome das classes do nosso problema (mesma ordem da anotação)
4.   `total_epochs`: número de épocas (iterações) a rodar o treino
5.   `learning_rate`: taxa de aprendizagem, o quanto vamos ajustar os valores dos filtros para tentar encontrar os melhores valores dos filtros. Geralmente é um valor bem pequeno 0.2 ... 0.001

> Esses dois últimos parâmetros (4. e 5.) podemos alterar para tentar melhorar o resultado do nosso algoritmo de detecção.


"""

import numpy as np
selected_model='detr_r50'
for size_bbox in np.arange(10,60,10):
  for f in np.arange(1,6):
    print('----------FOLD:',f)
    fold = 'fold_'+str(f)
    cfg = setCFG(selected_model=selected_model,data_root='/content/drive/MyDrive/Incendios/',classes=('Corn',),size_bbox=size_bbox,fold=fold)
    trainModel(cfg)
    print(selected_model)

cfg = setCFG(selected_model='atss_r50',data_root='/content/drive/MyDrive/IC',classes=('boca de lobo',)) #treinar modelo, mudar qnt de epoch na func
trainModel(cfg)
print(selected_model)

import numpy as np
selected_model='sabl_r50'
size_bbox=50
for f in np.arange(1,6):
  print('----------FOLD:',f)
  fold = 'fold_'+str(f)
  cfg = setCFG(selected_model=selected_model,data_root='/content/drive/MyDrive/Incendios/',classes=('Corn',),size_bbox=size_bbox,fold=fold)
  trainModel(cfg)
  print(selected_model)

import numpy as np
selected_model='sabl_r50'
size_bbox=30
for f in np.arange(1,6):
  print('----------FOLD:',f)
  fold = 'fold_'+str(f)
  cfg = setCFG(selected_model=selected_model,data_root='/content/drive/MyDrive/Incendios/',classes=('Corn',),size_bbox=size_bbox,fold=fold)
  trainModel(cfg)
  print(selected_model)

"""# Testando o modelo Treinado
> Na célula abaixo vamos iniciar a função que realizará o teste das imagens
"""

from mmdet.apis import inference_detector, init_detector, show_result_pyplot
from mmdet.datasets import replace_ImageToTensor
from mmdet.datasets import CocoDataset
from mmcv.visualization import color_val
from mmdet.core import visualization as vis

import mmcv, torch
import numpy as np
import cv2

from google.colab.patches import cv2_imshow

def testingModel(cfg=None,typeN='test',models_path=None,show_imgs=False,save_imgs=False):
  
  # build the model from a config file and a checkpoint file
  cfg.data.test.test_mode = True
  torch.backends.cudnn.benchmark = True
  cfg.model.pretrained = None

  modelx = init_detector(cfg, models_path)
  
  if typeN=='test':
    ann_file = cfg.data.test.ann_file
    img_prefix = cfg.data.test.img_prefix
    cfg.data.test.pipeline = replace_ImageToTensor(cfg.data.test.pipeline)
  elif typeN=='validation':
    ann_file = cfg.data.val.ann_file
    img_prefix = cfg.data.val.img_prefix  
  elif typeN=='train':
    ann_file = cfg.data.train.ann_file
    img_prefix = cfg.data.train.img_prefix  

  coco_dataset = CocoDataset(ann_file=ann_file, classes=cfg.classes,data_root=cfg.data_root,img_prefix=img_prefix,pipeline=cfg.train_pipeline,filter_empty_gt=False)

  results=[]
  for i,dt in enumerate(coco_dataset.data_infos):
    imagex=None
    imagex=mmcv.imread(os.path.join(coco_dataset.img_prefix,dt['file_name']))

    resultx = inference_detector(modelx, imagex)

    if show_imgs and i<10: ## VAI MOSTRAR APENAS 10 IMAGENS PARA NÃO FICAR LENTO!
      print(dt['file_name'])

      

      '''#GT BBOXS VERMELHOS      
      ann = coco_dataset.get_ann_info(i)
      bboxes = np.insert(ann['bboxes'],4,0.91,axis=1)

      vis.imshow_gt_det_bboxes(imagex,dict(gt_bboxes=bboxes, gt_labels=np.repeat(1, len(bboxes))), resultx, show=True,score_thr=0.5)

      for j in range(min(20, bboxes.shape[0])):
        left_top = (bboxes[j, 0], bboxes[j, 1])
        right_bottom = (bboxes[j, 2], bboxes[j, 3])
        imagex=cv2.rectangle(imagex, left_top, right_bottom, color_val('red'), thickness=2)'''
      
      #RESULTADOS BBOXS VERDES
      bboxes = resultx[0]
      for j in range(min(20, bboxes.shape[0])):
        left_top = (int(bboxes[j, 0]), int(bboxes[j, 1]))
        right_bottom = (int(bboxes[j, 2]), int(bboxes[j, 3]))
        imagex=cv2.rectangle(imagex, left_top, right_bottom, color_val('green'), thickness=1)
      
      cv2_imshow(imagex)#exportar img

    results.append(resultx)#exportar
  eval_results = coco_dataset.evaluate(results, classwise=True)#exportar metricas
  print(eval_results)
  #print(selected_model,'\t',eval_results['bbox_mAP_50'])
  string_results = selected_model+'\t'+str(eval_results['bbox_mAP_50'])
  return string_results

"""## Executando o teste e visualizando as imagens com as deteções
> Ao clicar na célula todas as imagens do conjunto de `test` serão executadas e mostrado as caixas preditas (cor verde) e as caixas da anotação (vermelha)

> É apresentado também o resultado de classificação em `category | AP` mostrado a taxa de acerto de cada classe. O maior valor é 1.0 (100% de acerto).
"""

pth ='/content/drive/MyDrive/IC/MModelsATSS_r101/atss_r50/epoch_12.pth' #pegar caminho da epoch
print(pth)
resAP50 = testingModel(cfg=cfg,typeN='test',models_path=pth,show_imgs=True)

