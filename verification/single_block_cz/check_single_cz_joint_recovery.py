"""Finite class-table certificate for conditional joint code/cycle recovery.

The block/edge normal form and whole-schedule composition are analytical;
this is NOT an exhaustive factory location-pair simulation.
"""
from pathlib import Path
from itertools import product,combinations_with_replacement
from collections import defaultdict
from hashlib import sha256
import argparse,json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/p) for p in ('src/single_block_cz','verification/single_block_cz','verification/shared')]
import c4_helix_single_block_cz as m
import single_cz_joint_recovery as joint
from single_cz_recovery import GRAPHS,data_table,STABILIZERS
from check_single_cz_root_recovery import verify_space,independent_word,dual_certificate
from check_single_cz_flags import certificate as flag_certificate
from check_single_cz_compact_checks import local_certificate


def independent_families(graph):
    cycle=lambda word:sum(((word & m.mask(c)).bit_count()%2) << j for j,c in enumerate(graph.cycles))
    cases={(None,0)} | {(v,0) for v in range(5)}
    cases |= {(v,1 << e) for v,e in enumerate(graph.tree,1)}
    cases |= {(None,1 << e) for e in range(len(graph.edges))}
    for v in range(1,5):
        es=[e for e,ends in enumerate(graph.edges) if v in ends]
        cases |= {(None,m.mask(es[j:])) for j in range(len(es)+1)}
    result=defaultdict(set)
    for (a,x),(b,y) in combinations_with_replacement(tuple(cases),2):
        result[cycle(x ^ y)].add(tuple(sorted({v for v in (a,b) if v is not None})))
    return {k:tuple(sorted(v)) for k,v in result.items()}


def block_words(block):
    words={}
    for x,z in product(range(16),repeat=2):
        pauli=(x << (4*block)) | (z << (20+4*block))
        words.setdefault(independent_word(pauli),pauli)
    assert len(words)==64
    return words


def template(blocks):
    result={0:0}
    for block in blocks:
        result={a ^ b:p ^ q for a,p in result.items() for b,q in block_words(block).items()}
    assert len(result)==64**len(blocks)
    return result


def audit():
    templates={};spaces={};graphs={}
    for graph in GRAPHS.values():
        families=joint.families(graph)
        assert families==independent_families(graph)
        for blocks in {b for fs in families.values() for b in fs}:
            if blocks not in templates:
                templates[blocks]=template(blocks)
                rank,classes,reports=verify_space(joint.data_space(blocks))
                spaces[str(blocks)]=dict(rank=rank,class_images=classes,syndrome_images=reports)
        contexts={}
        for cycle,family in families.items():contexts.setdefault(family,cycle)
        results=[]
        for family,cycle in contexts.items():
            expected=defaultdict(dict)
            for blocks in family:
                for word,p in templates[blocks].items():expected[word & ((1 << 18)-1)][word >> 18]=p
            unique=ambiguous=rescued=0
            for syndrome,labels in expected.items():
                row=joint.decision_word(graph,syndrome,cycle)
                assert row['classes']==len(labels)
                if len(labels)==1:
                    unique+=1;assert row['correction'] is not None
                    x,z=row['correction'];p=x | (z << 20)
                    assert independent_word(p)==syndrome | (next(iter(labels)) << 18)
                    q=next(iter(labels.values()));delta=p ^ q
                    assert delta & ((1 << 20)-1) in STABILIZERS and delta >> 20 in STABILIZERS
                    if data_table()[syndrome]['correction'] is None:rescued+=1
                else:
                    ambiguous+=1;assert row['correction'] is None and row['status']=='ambiguous'
            results.append(dict(cycle_representative=cycle,cycle_aliases=sum(fs==family for fs in families.values()),
                                block_families=[list(b) for b in family],syndrome_images=len(expected),
                                unique=unique,ambiguous=ambiguous,unique_where_data_only_rejects=rescued))
        # Cycle-zero data candidates contain every old unknown-two-block class.
        for syndrome,row in data_table().items():
            assert joint.decision_word(graph,syndrome,0)['classes']==row['classes']
        root_edges=[e for e,ends in enumerate(graph.edges) if 0 in ends]
        # Include cancelling nonzero flag pairs INSIDE ONE root gadget.
        # The opaque port audit bounds their union modulo the full Gauss
        # product by two ports; each remaining graph port is a single edge,
        # correlated with its data block exactly when it is a tree edge.
        root=flag_certificate(('W',)*4+('X',)*len(root_edges),m.SIGNS[:4]+(1,)*len(root_edges))
        graphs[graph.name]=dict(cycle_contexts=len(families),distinct_data_contexts=len(contexts),
                                zero_flag_root_support=root,contexts=results)
    paths=[Path(joint.__file__),Path(__file__),ROOT/'src/single_block_cz/single_cz_controller.py',
           ROOT/'src/single_block_cz/single_cz_root_recovery.py',
           ROOT/'src/single_block_cz/single_cz_flagged.py',
           ROOT/'src/single_block_cz/single_cz_compact_checks.py',
           ROOT/'src/single_block_cz/single_cz_recovery.py',
           ROOT/'src/single_block_cz/c4_helix_single_block_cz.py',
           ROOT/'verification/single_block_cz/check_single_cz_root_recovery.py',
           ROOT/'verification/single_block_cz/verify_single_block_cz_run.py',
           ROOT/'verification/single_block_cz/check_single_cz_flags.py',
           ROOT/'verification/single_block_cz/check_single_cz_compact_checks.py']
    return dict(verified=True,global_fault_budget=2,full_factory_location_pairs_enumerated=False,
                finite_scope='All typed one/two-cone compositions, every distinct affine syndrome image and ambiguity decision',
                analytical_scope='Physical block/edge normal form, certified nonzero trigger, conditional history and global terminal composition',
                known_block_spaces=spaces,graphs=graphs,
                zero_flag_compact_data_support=[local_certificate(axis,n) for axis,n in product('XZ',(4,8))],
                one_remaining_fault_conditional_support=dual_certificate(),
                source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/single-cz-joint-recovery-certificates.json')
    a=p.parse_args();result=audit();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    for name,row in result['graphs'].items():
        print(name,'cycle contexts',row['cycle_contexts'],'data contexts',row['distinct_data_contexts'],
              'rescued syndrome images',sum(c['unique_where_data_only_rejects'] for c in row['contexts']),flush=True)
    print('Saved',a.output)
