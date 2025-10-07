from data import AxesConfig


def get_relevant_axes(axes: AxesConfig.AxesConfig):
    '''from a list of AxesConfig Axes get the ones that have different start and stop values'''
    relevant_axes = []

    for axis in axes :
        if axis.start != axis.stop: # axis has some degree of positional change associated with it
            relevant_axes.append(axis)

    return relevant_axes

def get_step(axis: AxesConfig.Axis_Components):
    resolution = axis.resolution  #resolution of a step
    
    # Calculate step size: Step size is inversely proportional to resolution
    if (resolution < 2):
        resolution = 2 # Avoid zero resolution, which would lead to division by zero.
    
    start = axis.start  # Starting position
    stop = axis.stop  # Ending Position
    
    total_distance = stop - start
    
    if(total_distance == 0):
        return 0
    
    step_size = total_distance / (resolution - 1)
        
    # Adjust step direction
    step = step_size if start < stop else -step_size
    
    return step
    
def generate_linear_positions(axe_name, start, stop, step):
    position_instructions = []
    position = start
    
    # Loop through positions from start to stop, incrementing by the step size
    while (step > 0 and position <= stop) or (step < 0 and position >= stop):
        # Generate the G-code command for the current position
        position_instructions.append(f"{axe_name}{position:.3f}")
        
        # Move to the next position
        position += step
    
    return position_instructions

def create_command(command, instruction):
    return(f"{command} {instruction}\n")

def generate_snake_commands(axes: AxesConfig.AxesConfig, command = 'G0'):
    """create a set of gcode instructions from multiples Axes
    to move around a multi dimensional figure
    currently only supports 1-2 axis"""
    
    gcode_commands = []
    relevant_axes= get_relevant_axes(axes) #get the axes that have changes in position
    number_relevant_axes = len(relevant_axes) #quantity of axes that need to be moved

    if (number_relevant_axes == 0): #Nothing to Move
        gcode_commands.append("")

    elif (number_relevant_axes == 1): #Moving one Axis
        axe = relevant_axes[0]
        step = get_step(axe)
        positions = generate_linear_positions(axe.gCodeName, axe.start, axe.stop, step)
        for position in positions:
            gcode_commands.append(create_command(command, position))
    
    elif(number_relevant_axes == 2):
        
        axe1 = relevant_axes[0]
        axe2 = relevant_axes[1]
        #Get the two axis that need to be moved's positional changes
        axe1_step = get_step(axe1)
        axe1_positions = generate_linear_positions(axe1.gCodeName, axe1.start, axe1.stop, axe1_step)
        
        axe2_step_forward = get_step(axe2)
        axe2_step_backward = -axe2_step_forward
        
        axe2_positions_forward = generate_linear_positions(axe2.gCodeName, axe2.start, axe2.stop, axe2_step_forward)
        axe2_positions_backward = generate_linear_positions(axe2.gCodeName, axe2.stop, axe2.start, axe2_step_backward)

        forward = True
        
        for axe1_position in axe1_positions:
            if forward:  # If forward, use the forward positions of axe2
                forward = False
                # Set the initial position for axe1, and change the positions of axe2
                gcode_commands.append(create_command(command, f"{axe1_position} {axe2_positions_forward[0]}"))
                for axe2_position in axe2_positions_forward[1:]:  # Start from second position
                    gcode_commands.append(create_command("", axe2_position))
            else:  # If backward, use the backward positions of axe2
                forward = True
                # Change the positions of axe2 without repeating axe1
                gcode_commands.append(create_command(command, f"{axe1_position} {axe2_positions_backward[0]}"))
                for axe2_position in axe2_positions_backward[1:]:  # Start from second position
                    gcode_commands.append(create_command("", axe2_position))
            
    return gcode_commands