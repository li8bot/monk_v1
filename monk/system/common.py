from system.imports import *
from system.base_system_state import update_local_var



#############################################################################################################################
@accepts(str, verbose=[int, str, bool], post_trace=True)
@TraceFunction(trace_args=True, trace_rv=False)
def read_json(fname, verbose=0):
    with open(fname) as json_file:
        system_dict = json.load(json_file);
        system_dict["verbose"] = verbose;
    return system_dict;


@accepts(dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def write_json(system_dict):    
    fname = system_dict["fname"];
    f = open(fname, 'w');
    wr = json.dumps(system_dict, indent=4)
    f.write(wr);
    f.close();


@accepts(str, str, post_trace=True)
@TraceFunction(trace_args=True, trace_rv=False)
def parse_csv(fname, delimiter):
    f = open(fname);
    lst = f.readlines();
    f.close();
    del lst[0]
    img_list = [];
    label_list = [];
    for i in range(len(lst)):
        img, label = lst[i][:len(lst[i])-1].split(delimiter);
        img_list.append(img);
        label_list.append(label);
    classes = list(np.unique(sorted(label_list)))
    for i in range(len(lst)):
        label_list[i] = classes.index(label_list[i]);

    return img_list, label_list, classes;



def parse_csv2(fname, delimiter):
    df = pd.read_csv(fname, delimiter=delimiter);
    df = df.reindex(np.random.permutation(df.index));
    columns = df.columns;
    df[columns[1]] = df[columns[1]].astype(str);
    return df, columns;

#############################################################################################################################




#############################################################################################################################
@accepts(dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def save(system_dict):
    system_dict_copy = system_dict.copy();
    if(system_dict_copy["states"]["eval_infer"]):
        system_dict_tmp = read_json(system_dict_copy["fname"]);
        system_dict_tmp["testing"] = system_dict_copy["testing"];
        system_dict_tmp["dataset"]["test_path"] = system_dict_copy["dataset"]["test_path"];
        system_dict_tmp["dataset"]["transforms"]["test"] = system_dict_copy["dataset"]["transforms"]["test"];
        write_json(system_dict_tmp);  
    else:
        system_dict_copy = update_local_var(system_dict_copy);
        write_json(system_dict_copy);


#############################################################################################################################





#############################################################################################################################
#@accepts(str, post_trace=True)
@TraceFunction(trace_args=True, trace_rv=True)
def create_dir(dir_path):
    if(not os.path.isdir(dir_path)):
        os.mkdir(dir_path);  

#@accepts(str, post_trace=True)
@TraceFunction(trace_args=True, trace_rv=True)
def delete_dir(dir_path):
    if(os.path.isdir(dir_path)):
        shutil.rmtree(dir_path);

#############################################################################################################################