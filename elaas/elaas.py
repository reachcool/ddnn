from deepopt.deepopt import DeepOptEpoch
from .family.simple import SimpleHybridFamily

class Collection(object):
    def __init__(self, name, path="_models", nepochs=10):
        self.name = name
        self.path = path
        self.folder = '{}/{}'.format(self.path,name)
        
        self.searchspace = None
        self.set_model_family(SimpleHybridFamily)
        self.set_nepochs(nepochs)
            
    def set_nepochs(self, nepochs):
        self.nepochs = nepochs
        self.do = DeepOptEpoch(nepochs=nepochs, folder=self.folder)
        if self.searchspace is not None:
            self.set_searchspace(self.searchspace)
        
    def add_trainset(self, trainset):
        self.trainset = trainset

    def add_testset(self, testset):
        self.testset = testset
        
    def set_chooser(self, chooser):
        self.do.set_chooser(chooser)

    def set_model_family(self, family):
        self.family = family(folder=self.folder)

    def set_searchspace(self, **searchspace):
        self.searchspace = searchspace
        for k,v in searchspace.iteritems():
            self.do.add_param(k, v)

    def set_constraints(self, constraintfn):
        self.do.set_constraints(constraintfn)

    def train(self, niters=10, bootstrap_nepochs=2):
        do = self.do
        
        # Bootstrap epochs
        for point in do.get_bootstrap_points(bootstrap_nepochs):
            trainer, model = self.family.train_model(self.trainset, self.testset, **point)
            do.add_points(range(1,int(point['nepochs'])+1), trainer.get_log_result("validation/main/accuracy"), **point)
            
        do.fit()
        
        # Train
        for i in range(niters):
            point = self.do.sample_point()
            trainer, model = self.family.train_model(self.trainset, self.testset, **point)
            do.add_points(range(1, int(point['nepochs'])+1), trainer.get_log_result("validation/main/accuracy"), **point)
            do.fit()
            
        # Get the best model
        point = do.get_best_point()
        chain, model = self.family.load_chain_model(**point)

        # Associate with this collection
        self.model = model
        self.chain = chain
        return self.get_do_traces()

    def get_do_traces(self):
        return self.do.get_traces()
            
    def generate_c(self, in_shape):
        return self.model.generate_c(in_shape)

    def predict(self, x):
        return self.model(x)

    def generate_container(self):
        raise Exception("Not Implemented")
        #return self.model.generate_container_zip()