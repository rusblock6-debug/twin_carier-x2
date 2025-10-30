from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR


#  TODO: Вынести логику под каждый актор в отедльные управляющие классы
class TelemetryEmitter:
    def __init__(self, tick, data_callback):
        env = DR.env()
        writer = DR.writer()

        self.env = env
        self.tick = tick
        self.writer = writer
        self.data_callback = data_callback
        self.process = env.process(self.run())

    def run(self):
        while True:
            self.writer.writerow(self.data_callback())
            yield self.env.timeout(self.tick)
