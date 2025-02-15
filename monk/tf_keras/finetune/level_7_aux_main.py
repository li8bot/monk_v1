from tf_keras.finetune.imports import *
from system.imports import *

from tf_keras.finetune.level_6_params_main import prototype_params


class prototype_aux(prototype_params):
    @accepts("self", verbose=int, post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def __init__(self, verbose=1):
        super().__init__(verbose=verbose);


    ###############################################################################################################################################
    @accepts("self", show_img=bool, save_img=bool, check_missing=bool, check_corrupt=bool, post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def EDA(self, show_img=False, save_img=False, check_missing=False, check_corrupt=False):
        if(not self.system_dict["dataset"]["train_path"]):
            msg = "Dataset train path not set. Cannot run EDA";
            raise ConstraintError(msg);


        classes_folder, classes_folder_strength = class_imbalance(self.system_dict, show_img, save_img);
        missing_images_train, missing_images_val, corrupt_images_train, corrupt_images_val = corrupted_missing_images(self.system_dict, check_missing, check_corrupt);

        self.custom_print("EDA: Class imbalance")
        for i in range(len(classes_folder)):
            self.custom_print("    {}. Class: {}, Number: {}".format(i+1, classes_folder[i], classes_folder_strength[i]));
        self.custom_print("");

        if(check_missing):
            self.custom_print("EDA: Check Missing");
            if("csv" in self.system_dict["dataset"]["dataset_type"]):
                if(missing_images_train):
                    self.custom_print("    Missing Images in folder {}".format(self.system_dict["dataset"]["train_path"]));
                    for i in range(len(missing_images_train)):
                        self.custom_print("        {}. {}".format(i+1, missing_images_train[i]));
                    self.custom_print("");
                else:
                    self.custom_print("    All images present.");
                    self.custom_print("");

                if(missing_images_val):
                    self.custom_print("    Missing Images in folder {}".format(self.system_dict["dataset"]["val_path"]));
                    for i in range(len(missing_images_val)):
                        self.custom_print("        {}. {}".format(i+1, missing_images_val[i]));
                    self.custom_print("");
                else:
                    self.custom_print("    All images present.");
                    self.custom_print("");
            else:
                self.custom_print("    Missing check not required for foldered dataset");
                self.custom_print("");
            

        if(check_corrupt):
            self.custom_print("EDA: Check Corrupt");
            if(corrupt_images_train):
                self.custom_print("    Corrupt Images in folder {}".format(self.system_dict["dataset"]["train_path"]));
                for i in range(len(corrupt_images_train)):
                    self.custom_print("        {}. {}".format(i+1, corrupt_images_train[i]));
                self.custom_print("");
            else:
                self.custom_print("    No corrupt image found.");
                self.custom_print("");

            if(corrupt_images_val):
                self.custom_print("    Corrupt Images in folder {}".format(self.system_dict["dataset"]["val_path"]));
                for i in range(len(corrupt_images_val)):
                    self.custom_print("        {}. {}".format(i+1, corrupt_images_val[i]));
                self.custom_print("");
            else:
                self.custom_print("    No corrupt image found.");
                self.custom_print("");
    ###############################################################################################################################################




    ###############################################################################################################################################
    @warning_checks(None, num_epochs=["lt", 1000], post_trace=True)
    @error_checks(None, num_epochs=["gt", 0], post_trace=True)
    @accepts("self", num_epochs=[int, bool], post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def Estimate_Train_Time(self, num_epochs=False):
        self.system_dict = set_transform_estimate(self.system_dict);
        self.set_dataset_dataloader(estimate=True);
        total_time_per_epoch = self.get_training_estimate();
        self.custom_print("Training time estimate");
        if(not num_epochs):
            total_time = total_time_per_epoch*self.system_dict["hyper-parameters"]["num_epochs"];
            self.custom_print("    {} Epochs: Approx. {} Min".format(self.system_dict["hyper-parameters"]["num_epochs"], int(total_time//60)+1));
            self.custom_print("");
        else:
            total_time = total_time_per_epoch*num_epochs;
            self.custom_print("    {} Epochs: Approx. {} Min".format(num_epochs, int(total_time//60)+1));
            self.custom_print("");
    ###############################################################################################################################################





    ###############################################################################################################################################
    @error_checks(None, num=["gte", 0], post_trace=True)
    @accepts("self", num=int, post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def Freeze_Layers(self, num=10):
        self.num_freeze = num;
        self.system_dict = freeze_layers(num, self.system_dict);
        self.custom_print("Model params post freezing");
        self.custom_print("    Num trainable layers: {}".format(self.system_dict["model"]["params"]["num_params_to_update"]));
        self.custom_print("");
        save(self.system_dict);
    ###############################################################################################################################################



    ##########################################################################################################################################################
    @accepts("self", post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def Reload(self):
        if(self.system_dict["states"]["eval_infer"]):
            del self.system_dict["local"]["data_loaders"];
            self.system_dict["local"]["data_loaders"] = {};
            self.Dataset();
            del self.system_dict["local"]["model"];
            self.system_dict["local"]["model"] = False;
            self.Model();
        else:
            if(not self.system_dict["states"]["copy_from"]):
                del self.system_dict["local"]["model"];
                self.system_dict["local"]["model"] = False;
            del self.system_dict["local"]["data_loaders"];
            self.system_dict["local"]["data_loaders"] = {};
            self.Dataset();
            if(not self.system_dict["states"]["copy_from"]):
                self.Model();
                self.system_dict = load_scheduler(self.system_dict);
                self.system_dict = load_optimizer(self.system_dict);
                self.system_dict = load_loss(self.system_dict);
            if(self.system_dict["model"]["params"]["num_freeze"]):
                self.system_dict = freeze_layers(self.system_dict["model"]["params"]["num_freeze"], self.system_dict);
                self.custom_print("Model params post freezing");
                self.custom_print("    Num trainable layers: {}".format(self.system_dict["model"]["params"]["num_params_to_update"]));
                self.custom_print("");
                save(self.system_dict);
    ##########################################################################################################################################################




    ##########################################################################################################################################################
    @accepts("self", test=bool, post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def reset_transforms(self, test=False):
        tmp = {};
        tmp["featurewise_center"] = False;
        tmp["featurewise_std_normalization"] = False;
        tmp["rotation_range"] = 0;
        tmp["width_shift_range"] = 0;
        tmp["height_shift_range"] = 0;
        tmp["shear_range"] = 0;
        tmp["zoom_range"] = 0;
        tmp["brightness_range"] = None;
        tmp["horizontal_flip"] = False;
        tmp["vertical_flip"] = False;
        tmp["mean"] = False;
        tmp["std"] = False;

        
        if(self.system_dict["states"]["eval_infer"] or test):
            self.system_dict["local"]["transforms_test"] = tmp;
            self.system_dict["local"]["normalize"] = False;
            self.system_dict["local"]["mean_subtract"] = False;
            self.system_dict["dataset"]["transforms"]["test"] = [];
        else:
            self.system_dict["local"]["transforms_train"] = [];
            self.system_dict["local"]["transforms_val"] = [];
            self.system_dict["local"]["normalize"] = False;
            self.system_dict["local"]["mean_subtract"] = False;
            self.system_dict["local"]["transforms_train"] = tmp;
            self.system_dict["local"]["transforms_val"] = tmp;
        save(self.system_dict);
    ##########################################################################################################################################################





    ##########################################################################################################################################################
    @accepts("self", post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def reset_model(self):
        if(self.system_dict["states"]["copy_from"]):
            msg = "Cannot reset model in Copy-From mode.\n";
            raise ConstraintError(msg)
        self.system_dict["model"]["custom_network"] = [];
        self.system_dict["model"]["final_layer"] = None;
    ##########################################################################################################################################################





    ##########################################################################################################################################################
    @accepts("self", train=bool, eval_infer=bool, post_trace=True)
    @TraceFunction(trace_args=True, trace_rv=True)
    def Switch_Mode(self, train=False, eval_infer=False):
        if(eval_infer):
            self.system_dict["states"]["eval_infer"] = True;
        elif(train):
            self.system_dict["states"]["eval_infer"] = False;
    ##########################################################################################################################################################
