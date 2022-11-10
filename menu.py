import multiprocessing
from tkinter import *
from streamers import stream_myo
from unb_emg_toolbox.training_ui import TrainingUI
from unb_emg_toolbox.data_handler import OnlineDataHandler, OfflineDataHandler
from unb_emg_toolbox.utils import make_regex
from unb_emg_toolbox.feature_extractor import FeatureExtractor
from unb_emg_toolbox.emg_classifier import OnlineEMGClassifier
from isofitts import FittsLawTest

class Menu:
    def __init__(self):
        # Myo Streamer - start streaming the myo data 
        self.myo = multiprocessing.Process(target=stream_myo, daemon=True)
        self.myo.start()

        # Create online data handler to listen for the data
        self.odh = OnlineDataHandler(emg_arr=True)
        self.odh.get_data()

        self.classifier = None
        self.model_str = None

        self.window = None
        self.initialize_ui()
        self.window.mainloop()

    def initialize_ui(self):
        # Create the simple menu UI:
        self.window = Tk()
        if not self.model_str:
            self.model_str = StringVar(value='LDA')
        else:
            self.model_str = StringVar(value=self.model_str.get())
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.title("Game Menu")
        self.window.geometry("500x250")

        # Label 
        Label(self.window, font=("Arial bold", 20), text = 'UNB EMG Toolbox - Isofitts Demo').pack(pady=(10,20))
        # Train Model Button
        Button(self.window, font=("Arial", 18), text = 'Get Training Data', command=self.launch_training).pack(pady=(0,20))
        # Start Isofitts
        Button(self.window, font=("Arial", 18), text = 'Start Isofitts', command=self.start_test).pack()
        
        # Model Input
        frame = Frame(self.window)
        Label(self.window, text="Model:", font=("Arial bold", 18)).pack(in_=frame, side=LEFT, padx=(0,10))
        Entry(self.window, font=("Arial", 18), textvariable=self.model_str).pack(in_=frame, side=LEFT)
        frame.pack(pady=(20,10))
        # entry.grid(row=5, column=1, sticky=N+S+W+E, padx=(0,10))
            

    def start_test(self):
        self.window.destroy()
        self.set_up_classifier()
        FittsLawTest(num_trials=5).run()
        # Its important to stop the classifier after the game has ended
        # Otherwise it will continuously run in a seperate process
        self.classifier.stop_running()
        self.initialize_ui()

    def launch_training(self):
        self.window.destroy()
        # Launch training ui
        TrainingUI(num_reps=1, rep_time=5, rep_folder="classes/", output_folder="data/", data_handler=self.odh)
        self.initialize_ui()

    def set_up_classifier(self):
        WINDOW_SIZE = 25 
        WINDOW_INCREMENT = 5

        # Step 1: Parse offline training data
        dataset_folder = 'data/'
        classes_values = ["0","1","2","3","4"]
        classes_regex = make_regex(left_bound = "_C_", right_bound=".csv", values = classes_values)
        reps_values = ["0", "1", "2"]
        reps_regex = make_regex(left_bound = "R_", right_bound="_C_", values = reps_values)
        dic = {
            "reps": reps_values,
            "reps_regex": reps_regex,
            "classes": classes_values,
            "classes_regex": classes_regex
        }

        odh = OfflineDataHandler()
        odh.get_data(folder_location=dataset_folder, filename_dic=dic, delimiter=",")
        train_windows, train_metadata = odh.parse_windows(WINDOW_SIZE, WINDOW_INCREMENT)

        # Step 2: Extract features from offline data
        fe = FeatureExtractor(num_channels=8)
        feature_list = fe.get_feature_groups()['HTD']
        training_features = fe.extract_features(feature_list, train_windows)

        # Step 3: Dataset creation
        data_set = {}
        data_set['training_features'] = training_features
        data_set['training_labels'] = train_metadata['classes']

        # Step 4: Create online EMG classifier and start classifying.
        self.classifier = OnlineEMGClassifier(model=self.model_str.get(), data_set=data_set, num_channels=8, window_size=WINDOW_SIZE, window_increment=WINDOW_INCREMENT, 
                online_data_handler=self.odh, features=feature_list)
        self.classifier.run(block=False) # block set to false so it will run in a seperate process.

    def on_closing(self):
        # Clean up all the processes that have been started
        self.myo.terminate()
        self.odh.stop_data()
        self.window.destroy()

if __name__ == "__main__":
    menu = Menu()