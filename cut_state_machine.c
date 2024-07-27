#include "rtapi.h"          // API para la parte en tiempo real
#include "rtapi_app.h"      // API para la parte en tiempo real
#include "hal.h"            // API de HAL

#define MODNAME "cut_state_machine" // Nombre del módulo
#define PREFIX "cut_sm"             // Prefijo para los pines

MODULE_AUTHOR("Rene Bobey rbobey1989");
MODULE_DESCRIPTION("Hal component for cut_state_machine");
MODULE_LICENSE("GPL v2");

static int num_instances = 1; // Número de instancias del componente

typedef struct {

    hal_u32_t max_limit;            // Límite máximo de la máquina
    hal_u32_t min_limit;            // Límite mínimo de la máquina

    hal_bit_t *reset;               // Entrada de reset
    hal_u32_t *status;              // Salida de estado

    hal_float_t *cut_length;        // Entrada longitud de corte 
    hal_float_t *move_to_length;    // Salida de movimiento a
    hal_bit_t   *start_move;        // Salida de movimiento
    unsigned int width_start_move_pulse; // Contador de pulsos de inicio de movimiento
     

    hal_bit_t *start_cut;           // Entrada de inicio de corte

    unsigned int state;     // Estado actual de la máquina de estados
    unsigned int cut_length_value;  // Valor de longitud de corte 
    unsigned int current_cut_type;      // Tipo de corte actual 

    hal_bit_t *rigth_hand_button;   // Entrada pulsador derecho de manos ocupadas    
    hal_bit_t *left_hand_button;    // Entrada pulsador izquierdo de manos ocupadas
    hal_bit_t *clamps_button;       // Entrada pulsador de mordazas
    hal_bit_t *rigth_clamp;         // Salidas para mordaza derecha
    hal_bit_t *left_clamp;          // Salidas para mordaza izquierda
    hal_bit_t *rigth_head;          // Salidas para actuador neumático cabezal derecho
    hal_bit_t *left_head;           // Salidas para actuador neumático cabezal izquierdo
    hal_bit_t *feed_hold;           // Salida para control de movimiento
    hal_bit_t *feed_inhibit;        // Salida para control de movimiento
} cut_state_machine_t;

static cut_state_machine_t *cut_state_machine;


/* other globals */
int comp_id; // Identificador del componente
static const char *modname = MODNAME;
static const char 	*prefix = PREFIX;

// Estados de la máquina de estados
#define RESET -1
#define IDLE 0
#define REQUEST_USER_TO_PRESS_HANDS_BUSY_BUTTONS 1
#define WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED 2

#define SHORT_CUT 3


#define NORMAL_CUT 4


#define LONG_CUT 5


// Status
#define PRESS_HANDS_BUSY_BUTTONS    1
#define SHORT_CUT_TYPE              4
#define NORMAL_CUT_TYPE             5
#define LONG_CUT_TYPE               6

#define COUNT_START_MOVE_PULSE    100


/******************************************************************************
*               Decalracion de funciones locales                                                                            *   
******************************************************************************/

void update_cut_state_machine(void *arg, long period);

// Función para inicializar el componente
int rtapi_app_main(void) {
    char name[HAL_NAME_LEN + 1];
    int n, retval;

    comp_id = hal_init(modname);
    if (comp_id < 0){
        rtapi_print_msg(RTAPI_MSG_ERR, "%s ERROR: hal_init() failed \n", modname);
        return -1;
    }

    cut_state_machine = hal_malloc(sizeof(cut_state_machine_t));
    if (cut_state_machine == 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "ERROR: %s: hal_malloc() failed\n", modname);
        hal_exit(comp_id);
        return -1;
    }

    // Creación de los pines
    // Entradas

    retval = hal_param_u32_newf(HAL_RW, &(cut_state_machine->max_limit), comp_id, "%s.max-limit", prefix);
    if (retval != 0) goto error;

    retval = hal_param_u32_newf(HAL_RW, &(cut_state_machine->min_limit), comp_id, "%s.min-limit", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->reset), comp_id, "%s.reset", prefix);
    if (retval != 0) goto error;
    //*(cut_state_machine->reset) = 0;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->cut_length), comp_id, "%s.cut-length", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_OUT, &(cut_state_machine->move_to_length), comp_id, "%s.move-to-length", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->move_to_length) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->start_move), comp_id, "%s.start-move", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->start_move) = 0;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->start_cut), comp_id, "%s.start-cut", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->rigth_hand_button), comp_id, "%s.rigth-hand-button", prefix);
    if (retval != 0) goto error;
    //*(cut_state_machine->rigth_hand_button) = 0;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->left_hand_button), comp_id, "%s.left-hand-button", prefix);
    if (retval != 0) goto error;
    //*(cut_state_machine->left_hand_button) = 0;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->clamps_button), comp_id, "%s.clamps-button", prefix);
    if (retval != 0) goto error;
    //*(cut_state_machine->clamps_button) = 0;

    // Salidas

    retval = hal_pin_u32_newf(HAL_OUT, &(cut_state_machine->status), comp_id, "%s.status", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->status) = 0;
    cut_state_machine->state = IDLE;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->rigth_clamp), comp_id, "%s.rigth-clamp", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->rigth_clamp) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->left_clamp), comp_id, "%s.left-clamp", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_clamp) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->rigth_head), comp_id, "%s.rigth-head", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->rigth_head) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->left_head), comp_id, "%s.left-head", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_head) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->feed_hold), comp_id, "%s.feed-hold", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->feed_hold) = 1;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->feed_inhibit), comp_id, "%s.feed-inhibit", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->feed_inhibit) = 1;
    

	error:
	if (retval < 0) {
		rtapi_print_msg(RTAPI_MSG_ERR,
		        "%s: ERROR: pin export failed with err=%i\n",
		        modname, retval);
		hal_exit(comp_id);
		return -1;
	}

    // Exportar funciones
    rtapi_snprintf(name, sizeof(name), "%s.update-cut-sm", prefix);
    retval = hal_export_funct(name, update_cut_state_machine, cut_state_machine, 1, 0, comp_id);
    if (retval != 0) {
		rtapi_print_msg(RTAPI_MSG_ERR,
		        "%s: ERROR: update function export failed\n", modname);
		hal_exit(comp_id);
    }

    rtapi_print_msg(RTAPI_MSG_INFO, "%s: installed hal component\n", modname, num_instances);
    hal_ready(comp_id);
    return 0;
}

// Función para limpiar al salir
void rtapi_app_exit(void) {
    hal_exit(comp_id);
}

void update_cut_state_machine(void *arg, long period){

    cut_state_machine_t *cut_state_machine = (cut_state_machine_t *)arg;

    if (!(*(cut_state_machine->reset))) {
        *(cut_state_machine->status) = 0;
        *(cut_state_machine->rigth_clamp) = 0;
        *(cut_state_machine->left_clamp) = 0;
        *(cut_state_machine->rigth_head) = 0;
        *(cut_state_machine->left_head) = 0;
        *(cut_state_machine->feed_hold) = 1;
        *(cut_state_machine->feed_inhibit) = 1;

        cut_state_machine->state = IDLE;
    }
    else
    {
        switch (cut_state_machine->state)
        {
            case IDLE: 
                *(cut_state_machine->start_move) = 0;
                if (*(cut_state_machine->start_cut)) 
                {
                    cut_state_machine->cut_length_value = *(cut_state_machine->cut_length);

                    if (cut_state_machine->cut_length_value < cut_state_machine->min_limit)
                    {
                        cut_state_machine->current_cut_type = SHORT_CUT;
                    }
                    else if (cut_state_machine->cut_length_value >= cut_state_machine->min_limit && cut_state_machine->cut_length_value <= cut_state_machine->max_limit)
                    {
                        cut_state_machine->current_cut_type = NORMAL_CUT;
                    }
                    else
                    {
                        cut_state_machine->current_cut_type = LONG_CUT;
                    }

                    cut_state_machine->state = REQUEST_USER_TO_PRESS_HANDS_BUSY_BUTTONS;
                    
                }
                break;

            case REQUEST_USER_TO_PRESS_HANDS_BUSY_BUTTONS:
                *(cut_state_machine->status) = PRESS_HANDS_BUSY_BUTTONS;
                cut_state_machine->state = WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED;
                break;
                
            case WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED:
                if (!(*(cut_state_machine->rigth_hand_button)) && !(*(cut_state_machine->left_hand_button)))
                {
                    switch (cut_state_machine->current_cut_type)
                    {
                        case SHORT_CUT:
                            *(cut_state_machine->status) = SHORT_CUT_TYPE;
                            cut_state_machine->state = SHORT_CUT;
                            break;
                        case NORMAL_CUT:
                            *(cut_state_machine->status) = NORMAL_CUT_TYPE;
                            cut_state_machine->state = NORMAL_CUT;
                            break;
                        case LONG_CUT:
                            *(cut_state_machine->status) = LONG_CUT_TYPE;
                            cut_state_machine->state = LONG_CUT;
                            break;
                    }
                }
                break;

            case SHORT_CUT:

                break;

            case NORMAL_CUT:
                    *(cut_state_machine->move_to_length) = cut_state_machine->cut_length_value;
                    *(cut_state_machine->start_move) = 1; 
                    cut_state_machine->width_start_move_pulse++;
                    if (cut_state_machine->width_start_move_pulse == COUNT_START_MOVE_PULSE)
                    {
                        cut_state_machine->state = IDLE;
                        cut_state_machine->width_start_move_pulse = 0;
                    }
                    
                break;

            case LONG_CUT:

                break;
        }   

    }

    

}