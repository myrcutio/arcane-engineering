import inspect
import matplotlib.pyplot as plt
import numpy as np
from exceptions import *

class component():
    def __init__(self,requires_input = True, level = 1,energy = 0,name = 'placeholder_name'):
        self.requires_input = requires_input
        self.previous_comp = None #component before
        self.next_comp = None #component after
        self.energy = energy #amount of energy in the component
        self.level = level
        self.name = name
        self.allow_transfer = True
        #all components need a drawing function
        #   and also connecting points I think
        #   for now, let's just get them in one line
    def print_info(self):
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        passed_atts = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
        print(passed_atts)
    def step(self):
        #a placeholder
        pass

class Battery(component):
    def __init__(self,level = 1,energy = 100,name = "battery"):
        super().__init__(level = level,energy = energy,name = name)
        if level == 0:
            self.requires_input = False

    def plot(self,start_point = (0,0),x_size = 0.25,y_size = 1,ax = None):
        if ax is None:
            ax = plt.gca()
        line1_x = [start_point[0],
                   start_point[0]]
        line1_y = [start_point[1] - y_size/2,
                   start_point[1] +y_size/2]
        line2_x = [start_point[0]+x_size,
                   start_point[0]+x_size]
        line2_y = [start_point[1] - y_size/4,
                   start_point[1] + y_size/4]
        ax.plot(line1_x,line1_y,color = 'k',ls = "-")
        ax.plot(line2_x,line2_y,color = 'k',ls = "-")
        end_point = [start_point[0] + x_size,start_point[1]]
        return(end_point)

class Wire(component):
    def __init__(self,level = 1,energy = 0,name = "wire"):
        super().__init__(level = None,energy = energy,name = name)
        self.energy_in_rate = 1
        self.energy_out_rate = 1
        self.color = 'r'
    def step(self):
        
        if self.previous_comp.energy > 0 and self.previous_comp.allow_transfer:
            self.previous_comp.energy -=1
            self.energy += 1
        if self.energy > 0:
            self.next_comp.energy += 1
            self.energy -= 1
        # print("-------------")
        # print("wire: ",self.energy)
        # print("previous: ",self.previous_comp.energy)
        # print("next: ",self.next_comp.energy)
    def plot(self,start_point = [0,0],x_size = 3,y_size = 0,ax = None):
        if ax is None:
            ax = plt.gca()
        line1 = np.array([[start_point[0],start_point[0] + x_size],
                          [start_point[1],start_point[1] + y_size]])
        ax.plot(line1[0,:],line1[1,:],color = self.color,ls = "-")

        return(line1[:,1])
        
class Caster(component):
    def __init__(self,level = 1,energy = 0,name = "caster"):
        super().__init__(level = level,requires_input=True,energy = energy,name = name)
        self.cast_threshold = 100
        self.allow_transfer=False

    def cast(self):
        if self.energy>= self.cast_threshold:
            self.energy = 0
            return(True)
        else:
            return(False)
    
    def plot(self,start_point = (0,0),x_size = 1,y_size = 2,ax = None):
        if ax is None:
            ax = plt.gca()
        
        line1_x = [start_point[0],start_point[0] + x_size/2,start_point[0] + x_size]
        
        line1_y = [start_point[1],start_point[1] + y_size/2,start_point[1]]
        line2_y = [start_point[1],start_point[1] - y_size/2,start_point[1]]
        ax.plot(line1_x,line1_y,color = 'k',ls = "-")
        ax.plot(line1_x,line2_y,color = 'k',ls = "-")
        end_point = [start_point[0] + x_size,start_point[1]]

        return(end_point)
    
    def step(self):
        if self.energy >= self.cast_threshold:
            self.cast()
        else:
            pass
def connect(comp_list: list):
    n_components = len(comp_list)
    new_comp_list = []
    for i in range(n_components):
        print(i)
        j = (i+1)%n_components
        
        if comp_list[j].requires_input:
            wire_obj = Wire(None,0)
            comp_list[i].next_comp = wire_obj
            comp_list[j].previous_comp = wire_obj
            wire_obj.previous_comp = comp_list[i]
            wire_obj.next_comp = comp_list[j]
            wire_obj.level = wire_obj.previous_comp.level
            if wire_obj.level != wire_obj.next_comp.level:
                raise CircuitException(f"Wire object connecting {wire_obj.previous_comp.name} ({wire_obj.previous_comp.__class__.__name__}) and {wire_obj.next_comp.name} ({wire_obj.next_comp.__class__.__name__}) have different levels: {wire_obj.previous_comp.level} and {wire_obj.next_comp.level}")
            #comp_list[i].next_comp = comp_list[j]
            #comp_list[j].previous_comp = comp_list[i]
        else:
            comp_list[i].next_comp = None
    
        new_comp_list.append(comp_list[i])
        new_comp_list.append(wire_obj)
        #new_comp_list.append(comp_list[j])
    return(new_comp_list)
def wrap_around(end_point,wrap_to = [0,0],buffer = 3.,ax = None):
    if ax is None:
        ax = plt.gca()
    wire_line = np.array([[end_point[0],end_point[0] + buffer,end_point[0] + buffer,wrap_to[0] - buffer,wrap_to[0] - buffer,wrap_to[0]],
                          [end_point[1],end_point[1],end_point[1] - buffer,end_point[1] - buffer,end_point[1],end_point[1]]])
    ax.plot(wire_line[0],wire_line[1])

    

def plot(comp_list,buffer = 3.):
    n_components = len(comp_list)
    start_point = [0,0]
    start_point_init = start_point.copy()
    fig,ax = plt.subplots(1,1,figsize = (5,5))
    for i in range(n_components):
        end_point = comp_list[i].plot(start_point)
        start_point = np.array(end_point)# + np.array([buffer,0])
        #ax.plot([end_point[0],start_point[0],],[end_point[1],start_point[1],],c = 'r')

    wrap_around(end_point,wrap_to = start_point_init,buffer = buffer,ax = ax)
    plt.show()


if __name__ == "__main__":
    b_test = Battery(2,name = "Battery 1")
    c_test = Caster(2,name = "Caster 1")
    test_comp_list = [b_test,c_test]
    new_comp_list = connect(test_comp_list)
    #print(new_comp_list)
    
    #print(new_comp_list)
    b_test.print_info()
    c_test.print_info()
    #plot(new_comp_list)

    t = []
    E_battery = []
    E_caster = []
    for t_step in range(200):
        t.append(t_step)
        for comp in new_comp_list:
            comp.step()
        #print(b_test.energy)
        E_battery.append(b_test.energy)
        E_caster.append(c_test.energy)
    plt.plot(t,E_battery)
    plt.plot(t,E_caster)
    plt.show()
