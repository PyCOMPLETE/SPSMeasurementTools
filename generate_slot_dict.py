import myloadmat_to_obj as mlo

slot_mat = 'slots_s.mat'
slot_ob = mlo.myloadmat_to_obj(slot_mat)

s_vect = slot_ob.s_vect
n_vect = slot_ob.slot_n_vect

with open('slots_vs_s.py', 'w') as fid:
    for s in s_vect:
        fid.write('%.3f,\n'%s)
    fid.write('\n\n')

    for n in n_vect:
        fid.write('%d,\n'%n)
    fid.write('\n\n')

