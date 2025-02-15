from gluon.models.imports import *
from system.imports import *
from gluon.models.layers import get_layer


@accepts("self", bool, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def set_parameter_requires_grad(finetune_net, freeze_base_network):
    if(freeze_base_network):
        for param in finetune_net.collect_params().values():
            param.grad_req = 'null';
    return finetune_net


@accepts(dict, activation=str, post_trace=True)
@TraceFunction(trace_args=True, trace_rv=True)
def get_final_layer(network_layer, activation='relu'):
    act_list = ['relu', 'sigmoid', 'tanh', 'softrelu', 'softsign'];

    if(activation not in act_list):
        print("Final activation must be in set: {}".format(act_list));
        print("");
    else:
        layer = nn.Dense(network_layer["params"]["out_features"], weight_initializer=init.Xavier(), activation=activation);
        return layer;


@accepts("self", list, int, set=int, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def create_final_layer(finetune_net, custom_network, num_classes, set=1):
    last_layer_name = custom_network[len(custom_network)-1]["name"];

    if(set==1):
        if(last_layer_name == "linear"):
            with finetune_net.name_scope():
                for i in range(len(custom_network)-1):
                    layer = get_layer(custom_network[i]);
                    finetune_net.features.add(layer);
                    finetune_net.features[len(finetune_net.features)-1].initialize(init.Xavier(), ctx = ctx);
                finetune_net.output = get_layer(custom_network[len(custom_network)-1])
                finetune_net.output.initialize(init.Xavier(), ctx = ctx)
        else:
            with finetune_net.name_scope():
                for i in range(len(custom_network)-2):
                    layer = get_layer(custom_network[i]);
                    finetune_net.features.add(layer);
                    finetune_net.features[len(finetune_net.features)-1].initialize(init.Xavier(), ctx = ctx);
                finetune_net.output = get_final_layer(custom_network[len(custom_network)-2], activation=custom_network[len(custom_network)-1]['name']);
                finetune_net.output.initialize(init.Xavier(), ctx = ctx)


    if(set==2):
        net = nn.HybridSequential();
        with net.name_scope():
            for i in range(len(custom_network)):
                layer = get_layer(custom_network[i]);
                net.add(layer);
        with finetune_net.name_scope():
            finetune_net.output = net; 
            finetune_net.output.initialize(init.Xavier(), ctx = ctx) 


    if(set==3):
        msg = "Custom model addition for - Set 3 models: Not Implemented.\n";
        msg += "Set 3 models - {}\n".format(set3);
        msg += "Ignoring added layers\n";
        ConstraintWarning(msg);

    return finetune_net;



@accepts(dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def model_to_device(system_dict):

    if(system_dict["model"]["params"]["use_gpu"]):
        system_dict["local"]["ctx"] = [mx.gpu(0)];
    else:
        system_dict["local"]["ctx"] = [mx.cpu()];

    system_dict["local"]["model"].collect_params().reset_ctx(system_dict["local"]["ctx"])
    system_dict["local"]["model"].hybridize()

    return system_dict;


@accepts(dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def print_grad_stats(system_dict):
    print("Model - Gradient Statistics");
    i = 1;
    for param in system_dict["local"]["model"].collect_params().values():
        if(i%2 != 0):
            print("    {}. {} Trainable - {}".format(i//2+1, param, param.grad_req ));
        i += 1;
    print("");


@accepts(dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def get_num_layers(system_dict):
    num_layers = 0;
    for param in system_dict["local"]["model"].collect_params().values():
        num_layers += 1;
    system_dict["model"]["params"]["num_layers"] = num_layers//2;
    return system_dict;


@accepts(int, dict, post_trace=True)
@TraceFunction(trace_args=False, trace_rv=False)
def freeze_layers(num, system_dict):
    system_dict = get_num_layers(system_dict);
    num_layers_in_model = system_dict["model"]["params"]["num_layers"];
    if(num > num_layers_in_model):
        msg = "Parameter num > num_layers_in_model\n";
        msg += "Freezing entire network\n";
        msg += "TIP: Total layers: {}".format(num_layers_in_model);
        raise ConstraintError(msg)

    num = num*2;
    current_num = 0;
    value = 'null';

    for param in system_dict["local"]["model"].collect_params().values():
        param.grad_req = value;
        current_num += 1;
        if(current_num == num):
            value = 'write';

    params_to_update = [];
    for param in system_dict["local"]["model"].collect_params().values():
        if param.grad_req == 'write':
            params_to_update.append(param)
    system_dict["model"]["params"]["num_params_to_update"] = len(params_to_update)//2;
    system_dict["model"]["status"] = True;

    return system_dict;