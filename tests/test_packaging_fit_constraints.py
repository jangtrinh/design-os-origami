"""Flap endpoints must fit receiving material; lock holes must not overlap."""
import math
import unittest

from origami_cad import packaging
from origami_cad.fold_graph import contains, on_segment
from origami_cad.fold_kinematics import fold_vertices
from origami_cad.preview_model import build_preview_model
from dieline_topology import violations


def projected(points, axes):
    return [[p[i] for i in axes] for p in points]


def assert_flap_inside(test, cp, glue_point, receiver_point):
    model = build_preview_model(cp)
    test.assertTrue(model['available'], model['status'])
    glue = next(f for f in model['faces'] if contains(glue_point, f['vertices']))
    receiver = next(f for f in model['faces'] if contains(receiver_point, f['vertices']))
    folded = fold_vertices(model, 1)
    wall = folded[receiver['id']]
    spans = [max(p[i] for p in wall)-min(p[i] for p in wall) for i in range(3)]
    normal = spans.index(min(spans))
    test.assertLess(spans[normal], 1e-7, 'receiving tube panel must be planar')
    axes = [i for i in range(3) if i != normal]
    ring = projected(wall, axes)
    for p in folded[glue['id']]:
        test.assertAlmostEqual(p[normal], wall[0][normal], delta=1e-7)
        q = projected([p], axes)[0]
        test.assertTrue(contains(q, ring) or any(on_segment(q, a, b) for a, b in zip(ring, ring[1:]+ring[:1])),
                        f'flap endpoint {p} lies outside receiving panel {wall}')


class PackagingFitConstraints(unittest.TestCase):
    def accepted_or_constraint(self, generate, kwargs, constraint, check):
        try:
            cp = generate(**kwargs)
        except ValueError as error:
            self.assertRegex(str(error), constraint)
        else:
            check(cp)

    def test_small_sleeve_glue_endpoints_or_named_rejection(self):
        for kwargs in ({'height':5}, {'width':9,'depth':7,'height':4,'thickness':.3}):
            def check(blanks):
                cp = blanks[0];h=kwargs['height'];t=kwargs.get('thickness',.5);c=cp.calculate_score_allowance(90)
                w=kwargs.get('width',120)+2*t+2+c;side=h+t+2+c;band=kwargs.get('depth',80)+2*t
                assert_flap_inside(self,cp,[7.5,band/2],[15+2*w+1.5*side,band/2])
            with self.subTest(kwargs=kwargs):
                self.accepted_or_constraint(packaging.generate_sleeve_tray,kwargs,'glue_flap_width.*receiving',check)

    def test_small_0201_joint_endpoints_or_named_rejection(self):
        def check(cp):
            c=cp.calculate_score_allowance(90);l=100+c;b=20+c
            assert_flap_inside(self,cp,[15,30],[30+2*l+1.5*b,30])
        self.accepted_or_constraint(packaging.generate_fefco_0201,{'width':100,'depth':20,'height':60},
                                    'joint_flap_width.*receiving',check)

    def test_0427_overlapping_and_touching_slots_are_rejected(self):
        # strip=2: overlap below length6, and coincident CUT at length6.
        for width in (3,5.775,1,6):
            if width==6:
                cp=packaging.generate_fefco_0427(width=width)
                self.assertEqual(violations(cp)['cut_overlap'],[])
                continue
            with self.subTest(width=width), self.assertRaisesRegex(ValueError,'width.*lock slot.*gap'):
                packaging.generate_fefco_0427(width=width)

    def test_lock_slot_topology_if_generator_accepts_small_width(self):
        try:
            cp=packaging.generate_fefco_0427(width=3)
        except ValueError as error:
            self.assertRegex(str(error),'width.*lock slot.*gap')
        else:
            self.assertEqual(violations(cp)['cut_overlap'],[])

    def test_other_tube_generators_reject_oversized_flaps(self):
        for generate,kwargs in [(packaging.generate_tuck_box,{'width':10}),
                                (packaging.generate_crash_lock_box,{'width':10}),
                                (packaging.generate_gable_handle_box,{'width':10}),
                                (packaging.generate_pillow_box,{'depth':5})]:
            with self.subTest(generate=generate.__name__),self.assertRaisesRegex(ValueError,'glue_flap_width.*receiving'):
                generate(**kwargs)

    def test_valid_default_flap_endpoints_inside_receivers(self):
        for generate,kwargs,joint,w,d,h,first in [
            (packaging.generate_tuck_box,{},15,80,50,120,'d'),
            (packaging.generate_crash_lock_box,{},15,80,60,100,'d'),
            (packaging.generate_gable_handle_box,{},15,160,110,110,'d'),
            (packaging.generate_pillow_box,{},12,90,40,110,'w'),
            (packaging.generate_fefco_0201,{},30,200,150,120,'w'),
        ]:
            with self.subTest(generate=generate.__name__):
                cp=generate(**kwargs);c=cp.calculate_score_allowance(90);w+=c;d+=c
                receiver_x=joint+(2*d+1.5*w if first=='d' else 2*w+1.5*d)
                assert_flap_inside(self,cp,[joint/2,h/2],[receiver_x,h/2])

    def test_compatible_small_flaps_have_contained_endpoints(self):
        for h,w,d,t in [(5,120,80,.5),(4,9,7,.3)]:
            cp=packaging.generate_sleeve_tray(width=w,depth=d,height=h,thickness=t,glue_flap_width=5)[0]
            c=cp.calculate_score_allowance(90);span_w=w+2*t+2+c;span_h=h+t+2+c
            assert_flap_inside(self,cp,[2.5,(d+2*t)/2],[5+2*span_w+1.5*span_h,(d+2*t)/2])
            self.assertFalse(any(violations(cp).values()))
        cp=packaging.generate_fefco_0201(width=100,depth=20,height=60,joint_flap_width=20)
        c=cp.calculate_score_allowance(90)
        assert_flap_inside(self,cp,[10,30],[20+2*(100+c)+1.5*(20+c),30])
        self.assertFalse(any(violations(cp).values()))

    def test_slot_gap_boundary_varies_with_caliper_and_clearance(self):
        for t,clearance in [(0,1),(.5,1),(1.2,2)]:
            allowance=.45*t;strip=2*t+clearance;boundary=3*strip-allowance
            for delta in (-.01,0,5e-8):
                with self.subTest(t=t,delta=delta),self.assertRaisesRegex(ValueError,'width.*lock slot.*gap'):
                    packaging.generate_fefco_0427(width=boundary+delta,thickness=t,roll_clearance=clearance)
            cp=packaging.generate_fefco_0427(width=boundary+1e-5,thickness=t,roll_clearance=clearance)
            self.assertFalse(any(violations(cp).values()))

    def test_pillow_flap_contains_sampled_curve_breakpoints(self):
        for d,joint in [(40,30),(40,40.225),(20,10),(5,4)]:
            cp=packaging.generate_pillow_box(depth=d,glue_flap_width=joint)
            c=cp.calculate_score_allowance(90)
            assert_flap_inside(self,cp,[joint/2,55],[joint+2*(90+c)+1.5*(d+c),55])
            self.assertFalse(any(violations(cp).values()))

    def test_food_corner_glue_tabs_already_fit_the_receiver(self):
        for w,d,h,t in [(160,120,70,.5),(9,7,4,.3),(30,200,12,.6),(400,24,90,1.5)]:
            cp=packaging.generate_food_box(width=w,depth=d,height=h,thickness=t)
            c=cp.calculate_score_allowance(90);tab=min(h-1-t,(w+c)/2-t)
            assert_flap_inside(self,cp,[-h/2,-tab/2],[(w+c)/2,-h/2])
            assert_flap_inside(self,cp,[w+c+h/2,-tab/2],[(w+c)/2,-h/2])

    def test_explicit_flap_width_validation_and_equality(self):
        for generate,key in [(packaging.generate_tuck_box,'glue_flap_width'),
                             (packaging.generate_crash_lock_box,'glue_flap_width'),
                             (packaging.generate_pillow_box,'glue_flap_width'),
                             (packaging.generate_sleeve_tray,'glue_flap_width'),
                             (packaging.generate_fefco_0201,'joint_flap_width')]:
            for value in (float('nan'),float('inf'),-1,0,'15',True):
                with self.subTest(generator=generate.__name__,value=value),self.assertRaisesRegex(ValueError,key):
                    generate(**{key:value})

    def test_accepted_slot_gap_remains_topologically_resolvable(self):
        # Near-touching edges can coincide under the unchanged segment precision.
        for t,clearance in [(0,1),(.5,1),(1.2,2)]:
            strip=2*t+clearance;boundary=3*strip-.45*t
            for delta in (.75e-7*max(1,strip),1.5e-7,1.1e-7*max(1,strip),1e-5):
                try:
                    cp=packaging.generate_fefco_0427(width=boundary+delta,thickness=t,roll_clearance=clearance)
                except ValueError as error:
                    self.assertRegex(str(error),'width.*lock slot.*gap')
                else:
                    with self.subTest(t=t,delta=delta):
                        self.assertFalse(any(violations(cp).values()),violations(cp))

    def test_pillow_near_sample_breakpoint_does_not_create_micro_cuts(self):
        breakpoint=260.9/12
        for offset in (-1e-6,-1e-8,0,1e-8,1e-7,1e-6,2.5e-6,1e-5):
            joint=breakpoint+offset
            cp=packaging.generate_pillow_box(glue_flap_width=joint)
            with self.subTest(joint=joint):
                self.assertFalse(any(violations(cp).values()),violations(cp))
                self.assertTrue(build_preview_model(cp)['available'])
                c=cp.calculate_score_allowance(90)
                assert_flap_inside(self,cp,[joint/2,55],[joint+2*(90+c)+1.5*(40+c),55])

    def test_pillow_end_sample_cancellation_does_not_create_a_first_interval(self):
        for args in [dict(width=30,depth=200),
                     dict(width=30,depth=200,glue_flap_width=115.225),
                     dict(width=133.30370625307427,depth=36.61641248460995,thickness=0,
                          glue_flap_width=26.3733150901418)]:
            cp=packaging.generate_pillow_box(**args)
            with self.subTest(args=args):
                self.assertFalse(any(violations(cp).values()),violations(cp))
                self.assertTrue(build_preview_model(cp)['available'])
                c=cp.calculate_score_allowance(90);joint=args.get('glue_flap_width',12)
                assert_flap_inside(self,cp,[joint/2,55],
                                   [joint+2*(args['width']+c)+1.5*(args['depth']+c),55])


if __name__=='__main__':
    unittest.main()
