# Base Miner imports
from .base.miner import BaseMiner as BaseMiner
from .base.prompting_miner import BasePromptingMiner as BasePromptingMiner

# Miner imports.
from .text_to_text.template.miner import TemplateMiner as TemplateMiner
from .text_to_text.gpt4all.miner import GPT4ALLMiner as GPT4ALLMiner
from .text_to_text.AI21.miner import AI21Miner as AI21Miner
from .text_to_text.AlephAlpha.miner import AlephAlphaMiner as AlephAlphaMiner
from .text_to_text.bloom.miner import BloomChatMiner as BloomChatMiner
from .text_to_text.cohere.miner import CohereMiner as CohereMiner
from .text_to_text.gooseai.miner import GooseMiner as GooseMiner
from .text_to_text.koala.miner import KoalaMiner as KoalaMiner
from .text_to_text.llama.miner import LlamaMiner as LlamaMiner
from .text_to_text.neoxt.miner import NeoxtMiner as NeoxtMiner
from .text_to_text.openai.miner import OpenAIMiner as OpenAIMiner
from .text_to_text.pythia.miner import PythiaMiner as PythiaMiner
from .text_to_text.robertmyers.miner import RobertMyersMiner as RobertMyersMiner
from .text_to_text.stabilityai.miner import StabilityAIMiner as StabilityAIMiner
from .text_to_text.vicuna.miner import VicunaMiner as VicunaMiner
from .text_to_text.cerebras.miner import CerebrasMiner as CerebrasMiner
from .text_to_text.falcon.miner import FalconMiner as FalconMiner
from .text_to_text.hermes.miner import HermesMiner as HermesMiner
from .text_to_text.bittensor_lm.miner import CerebrasBTLMMiner as BittensorLMMiner

# Lower case imports
from .text_to_text.template.miner import TemplateMiner as template
from .text_to_text.gpt4all.miner import GPT4ALLMiner as gpt4all
from .text_to_text.AI21.miner import AI21Miner as ai21
from .text_to_text.AlephAlpha.miner import AlephAlphaMiner as alephalpha
from .text_to_text.bloom.miner import BloomChatMiner as bloom
from .text_to_text.cohere.miner import CohereMiner as cohere
from .text_to_text.gooseai.miner import GooseMiner as goose
from .text_to_text.koala.miner import KoalaMiner as koala
from .text_to_text.llama.miner import LlamaMiner as llama
from .text_to_text.neoxt.miner import NeoxtMiner as neoxt
from .text_to_text.openai.miner import OpenAIMiner as openai
from .text_to_text.pythia.miner import PythiaMiner as pythia
from .text_to_text.robertmyers.miner import RobertMyersMiner as robert
from .text_to_text.stabilityai.miner import StabilityAIMiner as stability
from .text_to_text.vicuna.miner import VicunaMiner as vicuna
from .text_to_text.cerebras.miner import CerebrasMiner as cerebras
from .text_to_text.falcon.miner import FalconMiner as falcon
from .text_to_text.hermes.miner import HermesMiner as HermesMiner
from .text_to_text.bittensor_lm.miner import CerebrasBTLMMiner as bittensor_lm
