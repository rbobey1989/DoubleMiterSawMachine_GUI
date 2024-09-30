#include "rtapi.h"          // API para la parte en tiempo real
#include "rtapi_app.h"      // API para la parte en tiempo real
#include "hal.h"            // API de HAL
#include "math.h"           // Librería de funciones matemáticas
#include <stdint.h>
#include <stdbool.h>

#define MODNAME "cut_state_machine" // Nombre del módulo
#define PREFIX "cut_sm"             // Prefijo para los pines

MODULE_AUTHOR("Rene Bobey rbobey1989");
MODULE_DESCRIPTION("Hal component for cut_state_machine");
MODULE_LICENSE("GPL v2");

static int num_instances = 1; // Número de instancias del componente

typedef struct {
    uint8_t out;
    bool both;
    bool in_edge;
    int pulse_count;
    uint32_t out_width_pulses;
    uint8_t last_in;
    bool first;
} edge_detector_t;

typedef struct {

    hal_u32_t           max_limit;                                  // Límite máximo de la máquina
    hal_u32_t           min_limit;                                  // Límite mínimo de la máquina
    hal_float_t         ferror;                                     // Entrada longitud de corte
    hal_bit_t           angle_head_type_actuator;                   // Tipo de actuador para posicionamiento de cabezales
    hal_float_t         min_cut_top_position;                       // Posición del tope mínimo

    hal_bit_t           *estop;                                     // Entrada de estop
    hal_u32_t           *status;                                    // Salida de estado
    hal_bit_t           *feed_inhibit;                              // Salida de feed hold
    hal_bit_t           *homing;                                    // Entrada de homing
    hal_bit_t           *homing_start;                              // Entrada de inicio de homing
    hal_bit_t           *homing_break_deactivate;                   // Salida desactivación de freno en homing

    hal_float_t         *pos_fb;                                    // Entrada longitud de corte

    hal_bit_t           *in_pos;                                    // Entrada de realimentación de posición
    hal_float_t         *bottom_cut_length;                         // Entrada longitud de corte inferior
    hal_float_t         *top_cut_length;                            // Entrada longitud de corte superior
    hal_float_t         *height_cut_length;                                // Entrada altura de corte
    hal_float_t         *cut_left_angle;                            // Entrada Posición cabezal izquierdo
    hal_float_t         *cut_right_angle;                           // Entrada Posición cabezal derecho
    hal_float_t         *move_to_length;                            // Salida de movimiento a
    hal_bit_t           *start_cut;                                 // Entrada de inicio de corte
    hal_bit_t           *start_move;                                // Salida de movimiento
    hal_bit_t           *stop_move;                                 // Entrada de paro de movimiento
    hal_bit_t           *cut_complete;                              // Salida de corte completo

    hal_bit_t           *left_saw_blade_btn;                                          // Entrada para disco de corte izquierdo
    hal_bit_t           *left_saw_blade;                                              // Salida para disco de corte izquierdo

    hal_bit_t           *right_saw_blade_btn;                                         // Entrada para disco de corte derecho
    hal_bit_t           *right_saw_blade;                                             // Salida para disco de corte derecho

    hal_bit_t           *clamps_button;                                           // Entrada pulsador de mordazas
    edge_detector_t     rising_edge_detector_clamps_btn;                          // Estructura para debounce de pulsador de mordazas
    edge_detector_t     falling_edge_detector_clamps_btn;                         // Estructura para debounce de pulsador de mordazas
    hal_bit_t           edge_detector_clamps_btn_both;                            // Parametro seleccion de deteccion ambos flancos del pulsador de mordazas
    hal_bit_t           edge_detector_clamps_btn_in_edge;                         // Parametro seleccion de flanco del pulsador de mordazas
    hal_u32_t           edge_detector_clamps_btn_out_width_pulses;                // Parametro ancho de pulso de salida del pulsador de mordazas
    bool                clamps_button_state;                                      // Valor del pulsador de mordazas

    hal_float_t         *saw_blade_output_time;                 // Tiempo de salida disco de corte
    hal_u32_t           *number_of_cuts;                        // Número de cortes
    hal_u32_t           number_of_cuts_value;                   // Valor de número de cortes

    uint16_t            delay_count;                            // Contador de pulsos de inicio de movimiento
    uint16_t            delay_count_left_saw_blade;
    uint16_t            delay_count_right_saw_blade;
    uint16_t            delay_count_break;
    
    uint8_t             state;                                  // Estado actual de la máquina de estados
    float               bottom_cut_length_value;                // Valor de longitud de corte inferior 
    float               top_cut_length_value;                   // Valor de longitud de corte superior
    float               height_cut_value;                       // Valor de altura de corte
    uint8_t             current_cut_type;                       // Tipo de corte actual

    float               left_head_pos_value;                    // Valor de posición de cabezal izquierdo
    float               right_head_pos_value;                   // Valor de posición de cabezal derecho

    bool                init_left_cut;                          // Inicio de corte izquierdo
    bool                init_right_cut;                         // Inicio de corte derecho
    bool                end_cut;                                // Fin de corte

    hal_bit_t           *busy_hand_btns;                                    // Entrada pulsador derecho de manos ocupadas
    edge_detector_t     rising_edge_detector_busy_hand_btns;                // Estructura para deteccion de bordes de pulsador derecho de disco derecho
    edge_detector_t     falling_edge_detector_busy_hand_btns;               // Estructura para deteccion de bordes de pulsador derecho de disco derecho
    hal_bit_t           edge_detector_busy_hand_btns_both;                  // Parametro seleccion de deteccion ambos flancos del pulsador derecho de disco derecho
    hal_bit_t           edge_detector_busy_hand_btns_in_edge;               // Parametro seleccion de flanco del pulsador derecho de disco derecho
    hal_u32_t           edge_detector_busy_hand_btns_out_width_pulses;      // Parametro ancho de pulso de salida del pulsador derecho de disco derecho
    bool                busy_hand_btns_state;                               // Valor del pulsador derecho de manos ocupadas

    hal_bit_t           *right_clamp;                   // Salidas para mordaza derecha
    hal_bit_t           *left_clamp;                    // Salidas para mordaza izquierda
    
    hal_bit_t           *right_head;                    // Salidas para actuador neumático cabezal derecho
    hal_bit_t           *left_head;                     // Salidas para actuador neumático cabezal izquierdo
    
    hal_bit_t           *left_saw_blade_output_move;    // Salida para movimiento de disco de corte izquierdo     
    hal_bit_t           *right_saw_blade_output_move;   // Salida para movimiento de disco de corte derecho

    hal_bit_t           *breaks;                        // Salida para freno
    uint8_t             break_state;                    // Estado de freno
    bool                break_nedded;                   // Freno necesario

} cut_state_machine_t;


static cut_state_machine_t *cut_state_machine;          // Estructura de la máquina de estados
bool init_params_edge_detector = false;                 // Inicialización de parámetros de edge detector
bool wait_for_msg = false;                              // Espera de mensaje
uint8_t step_long_cut = 0;                              // Paso de corte largo
bool skip_cut = false;                                  // Salto de corte


/* other globals */
int comp_id; // Identificador del componente
static const char *modname = MODNAME;
static const char 	*prefix = PREFIX;

// Estados de la máquina de estados
#define IDLE                                                                            0
#define REQUEST_USER_TO_PRESS_HANDS_BUSY_BUTTONS                                        1
#define WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_START_MOVE                      2
#define POSITIONING_HEAD_ANGLES                                                         3
#define SHORT_CUT                                                                       4
#define NORMAL_CUT                                                                      5
#define LONG_CUT                                                                        6
#define WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL                                         7
#define WAITING_FOR_LOW_LEVEL_IN_POS_SIGNAL                                             8
#define WAITING_FOR_MACHINE_IN_POSITION                                                 9
#define WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED                                         10
#define CHECK_VISUALLY_CONTROLLED_CONTROLLED_CUTTING_BY_THE_OPERATOR_OR_BY_TIME         11
#define WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_CUT                             12
#define CUT_COMPLETE_SEND_PULSE                                                         13
#define SELECT_CUT_TYPE                                                                 14
#define SAW_BLADE_OUTPUT_CONTROLLED_BY_TIME                                             15
#define SAW_BLADE_OUTPUT_CONTROLLED_BY_USER                                             16
#define CHANGE_STATE_CLAMPS_LONG_CUT_FOR_STEP_1_2                                       17
#define DELAY_OPEN_CLAMPS                                                               18
#define SEND_CUT_COMPLETE_MSG                                                           19
#define DEACTIVATE_BREAK                                                                20
#define ACTIVATE_BREAK                                                                  21


#define WAITING_FOR_BREAK_TO_BE_DEACTIVATED                                             1
#define WAITING_FOR_BREAK_TO_BE_ACTIVATED_WORK_MODE                                     2
#define WAITING_FOR_BREAK_TO_BE_ACTIVATED_HOMING_MODE                                   3
#define WAITING_FOR_HOMING_START_LOW_LEVEL                                              4
#define BREAK_ACTIVATED                                                                 5

// Status
#define PRESS_HANDS_BUSY_BUTTONS_FOR_MOVE                               1
#define POSITION_PROFILE_AND_CLOSE_CLAMPS                               2
#define CUT_COMPLETE                                                    3
#define SHORT_CUT_TYPE                                                  4
#define NORMAL_CUT_TYPE                                                 5
#define LONG_CUT_TYPE                                                   6
#define PRESS_BUSY_HANDS_BUTTONS_FOR_CUT                                7
#define CLOSE_CLAMPS                                                    8
#define POSITIONING_HEADS                                               10
#define THERE_ARE_NO_PIECES_TO_CUT                                      11
#define TURN_ON_SAW_BLADES_AND_PRESS_HANDS_BUSY_BUTTONS                 12
#define CUT_ONLY_LEFT_SAW_BLADE                                         13
#define CUT_ONLY_RIGHT_SAW_BLADE                                        14
#define CUT_BOTH_SAW_BLADES                                             15
#define CUT_CONTROLLED_BY_TIME                                          16
#define CUT_CONTROLLED_BY_USER                                          17
#define TURN_ON_RIGHT_SAW_BLADE_AND_PRESS_HANDS_BUSY_BUTTONS            18
#define TURN_ON_LEFT_SAW_BLADE_AND_PRESS_HANDS_BUSY_BUTTONS             19
#define CUT_ONLY_RIGHT_SAW_BLADE_SHORT_CUT                              20
#define PRESS_BUSY_HAND_BTNS_FOR_MOVE_TO_RECOVER_LENGTH_LONG_CUT        21
#define PRESS_BUSY_HAND_BTNS_FOR_MOVE_TO_FINISH_LONG_CUT                22


// Type Head Actuator
#define PNEUMATIC_ACTUATOR 0
#define SERVO_ACTUATOR 1

#define COUNT_PULSE                         120
#define COUNT_MSG                           100
#define COUNT_CLAMP_OPEN_LONG_CUT           1000
#define COUNT_CLAMP_OPEN                    500
#define COUNT_BREAK                         1000


/******************************************************************************
*               Decalracion de funciones locales                                                                            *   
******************************************************************************/

void update_cut_state_machine(void *arg, long period);
void edges_detection_update(void *arg, long period);
uint8_t edge_detector(edge_detector_t *detector, uint8_t in_signal_value);

/*****************************************************************************/
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

    retval = hal_param_float_newf(HAL_RW, &(cut_state_machine->ferror), comp_id, "%s.ferror", prefix);
    if (retval != 0) goto error;

    retval = hal_param_bit_newf(HAL_RW, &(cut_state_machine->angle_head_type_actuator), comp_id, "%s.angle-head-type-actuator", prefix);
    if (retval != 0) goto error;

    retval = hal_param_float_newf(HAL_RW, &(cut_state_machine->min_cut_top_position), comp_id, "%s.min-cut-top-position", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->estop), comp_id, "%s.estop", prefix);
    if (retval != 0) goto error;
    //*(cut_state_machine->estop) = 0;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->pos_fb), comp_id, "%s.pos-fb", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->in_pos), comp_id, "%s.in_pos", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->top_cut_length), comp_id, "%s.top-cut-length", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->bottom_cut_length), comp_id, "%s.bottom-cut-length", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->height_cut_length), comp_id, "%s.height-cut-length", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->cut_left_angle), comp_id, "%s.cut-left-angle", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->cut_right_angle), comp_id, "%s.cut-right-angle", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_float_newf(HAL_OUT, &(cut_state_machine->move_to_length), comp_id, "%s.move-to-length", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->move_to_length) = 0;

    retval = hal_pin_bit_newf(HAL_IO, &(cut_state_machine->start_move), comp_id, "%s.start-move", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->start_move) = 0;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->stop_move), comp_id, "%s.stop-move", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IO, &(cut_state_machine->cut_complete), comp_id, "%s.cut-complete", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->cut_complete) = 0;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->start_cut), comp_id, "%s.start-cut", prefix);
    if (retval != 0) goto error;

    /*********************************************************************************************
     *                     Inicializacion del pulsadorres de manos ocupadas                      *
     *********************************************************************************************/

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->busy_hand_btns), comp_id, "%s.busy-hand-btns", prefix);
    if (retval != 0) goto error;

    retval = hal_param_bit_newf(HAL_RW, &(cut_state_machine->edge_detector_busy_hand_btns_both), comp_id, "%s.busy-hand-btns-both", prefix);
    if (retval != 0) goto error;

    retval = hal_param_bit_newf(HAL_RW, &(cut_state_machine->edge_detector_busy_hand_btns_in_edge), comp_id, "%s.busy-hand-btns-in-edge", prefix);
    if (retval != 0) goto error;

    retval = hal_param_u32_newf(HAL_RW, &(cut_state_machine->edge_detector_busy_hand_btns_out_width_pulses), comp_id, "%s.busy-hand-btns-out-width-pulses", prefix);
    if (retval != 0) goto error;

    cut_state_machine->rising_edge_detector_busy_hand_btns.first = true;
    cut_state_machine->falling_edge_detector_busy_hand_btns.first = true;

    /*********************************************************************************************
     *                     Inicializacion del pulsador de mordazas                                *
     *********************************************************************************************/

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->clamps_button), comp_id, "%s.clamps-button", prefix);
    if (retval != 0) goto error;

    retval = hal_param_bit_newf(HAL_RW, &(cut_state_machine->edge_detector_clamps_btn_both), comp_id, "%s.clamps-btn-both", prefix);
    if (retval != 0) goto error;

    retval = hal_param_bit_newf(HAL_RW, &(cut_state_machine->edge_detector_clamps_btn_in_edge), comp_id, "%s.clamps-btn-in-edge", prefix);
    if (retval != 0) goto error;

    retval = hal_param_u32_newf(HAL_RW, &(cut_state_machine->edge_detector_clamps_btn_out_width_pulses), comp_id, "%s.clamps-btn-out-width-pulses", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IO, &(cut_state_machine->right_clamp), comp_id, "%s.right-clamp", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->right_clamp) = 0;

    retval = hal_pin_bit_newf(HAL_IO, &(cut_state_machine->left_clamp), comp_id, "%s.left-clamp", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_clamp) = 0;

    cut_state_machine->rising_edge_detector_clamps_btn.first = true;
    cut_state_machine->falling_edge_detector_clamps_btn.first = true;
    
    /*********************************************************************************************
     *                                                                                           *
     *********************************************************************************************/

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->right_saw_blade_btn), comp_id, "%s.right-saw-blade-btn", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->right_saw_blade), comp_id, "%s.right-saw-blade", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->right_saw_blade) = 0;

    /*********************************************************************************************
     *                                                                                           *
     *********************************************************************************************/

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->left_saw_blade_btn), comp_id, "%s.left-saw-blade-btn", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->left_saw_blade), comp_id, "%s.left-saw-blade", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_saw_blade) = 0;

    /*********************************************************************************************
     *                                                                                           *
     *********************************************************************************************/

    retval = hal_pin_float_newf(HAL_IN, &(cut_state_machine->saw_blade_output_time), comp_id, "%s.saw-blade-output-time", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_u32_newf(HAL_IO, &(cut_state_machine->number_of_cuts), comp_id, "%s.number-of-cuts", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->number_of_cuts) = 0;

    // Salidas

    retval = hal_pin_u32_newf(HAL_OUT, &(cut_state_machine->status), comp_id, "%s.status", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->status) = 0;
    cut_state_machine->state = IDLE;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->feed_inhibit), comp_id, "%s.feed-inhibit", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->feed_inhibit) = 1;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->homing), comp_id, "%s.homing", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_IN, &(cut_state_machine->homing_start), comp_id, "%s.homing-start", prefix);
    if (retval != 0) goto error;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->homing_break_deactivate), comp_id, "%s.homing-break-deactivate", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->homing_break_deactivate) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->right_head), comp_id, "%s.right-head", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->right_head) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->left_head), comp_id, "%s.left-head", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_head) = 0;

    /*********************************************************************************************
     *                                                                                           *
     *********************************************************************************************/

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->left_saw_blade_output_move), comp_id, "%s.left-saw-blade-output-move", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->left_saw_blade_output_move) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->right_saw_blade_output_move), comp_id, "%s.right-saw-blade-output-move", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->right_saw_blade_output_move) = 0;

    retval = hal_pin_bit_newf(HAL_OUT, &(cut_state_machine->breaks), comp_id, "%s.breaks", prefix);
    if (retval != 0) goto error;
    *(cut_state_machine->breaks) = 0;
    cut_state_machine->break_state = WAITING_FOR_BREAK_TO_BE_DEACTIVATED;
    cut_state_machine->break_nedded = false;
    cut_state_machine->delay_count_break = 0;


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

    rtapi_snprintf(name, sizeof(name), "%s.edges-detection-update", prefix);
    retval = hal_export_funct(name, edges_detection_update, cut_state_machine, 1, 0, comp_id);
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

    if (!*(cut_state_machine->estop) || *(cut_state_machine->stop_move))
    {
        *(cut_state_machine->status) = 0;
        *(cut_state_machine->right_clamp) = 0;
        *(cut_state_machine->left_clamp) = 0;
        *(cut_state_machine->right_head) = 0;
        *(cut_state_machine->left_head) = 0;
        *(cut_state_machine->left_saw_blade) = 0;
        *(cut_state_machine->right_saw_blade) = 0;
        *(cut_state_machine->left_saw_blade_output_move) = 0;
        *(cut_state_machine->right_saw_blade_output_move) = 0;
        *(cut_state_machine->feed_inhibit) = 1;
        *(cut_state_machine->homing_break_deactivate) = 0;
        cut_state_machine->delay_count = 0;
        cut_state_machine->delay_count_left_saw_blade = 0;
        cut_state_machine->delay_count_right_saw_blade = 0;
        *(cut_state_machine->breaks) = 0;
        cut_state_machine->break_nedded = false;
        cut_state_machine->delay_count_break = 0;
        cut_state_machine->busy_hand_btns_state = false;
        cut_state_machine->clamps_button_state = false;
        cut_state_machine->init_left_cut = false;
        cut_state_machine->init_right_cut = false;
        *(cut_state_machine->start_move) = 0;
        *(cut_state_machine->stop_move) = 0;
        step_long_cut = 0;

        cut_state_machine->state = IDLE;
    }
    else
    { 

        if (*(cut_state_machine->left_saw_blade_btn))
        {
            *(cut_state_machine->left_saw_blade) = 1;
        }
        else
        {
            *(cut_state_machine->left_saw_blade) = 0;
        }

        if (*(cut_state_machine->right_saw_blade_btn))
        {
            *(cut_state_machine->right_saw_blade) = 1;
        }
        else
        {
            *(cut_state_machine->right_saw_blade) = 0;
        }

        switch (cut_state_machine->state)
        {
            
            case IDLE:

                cut_state_machine->number_of_cuts_value = *(cut_state_machine->number_of_cuts);

                if (cut_state_machine->number_of_cuts_value > 0)
                {
                    if (*(cut_state_machine->start_cut))
                    {
                        if ((cut_state_machine->bottom_cut_length_value == *(cut_state_machine->bottom_cut_length)) && 
                            (cut_state_machine->top_cut_length_value == *(cut_state_machine->top_cut_length)) &&
                            (cut_state_machine->height_cut_value == *(cut_state_machine->height_cut_length)) &&
                            (cut_state_machine->left_head_pos_value == *(cut_state_machine->cut_left_angle)) &&
                            (cut_state_machine->right_head_pos_value == *(cut_state_machine->cut_right_angle)))
                        {
                            cut_state_machine->state = SELECT_CUT_TYPE;
                        }
                        else
                        {
                            cut_state_machine->bottom_cut_length_value = *(cut_state_machine->bottom_cut_length);
                            cut_state_machine->top_cut_length_value = *(cut_state_machine->top_cut_length);
                            cut_state_machine->height_cut_value = *(cut_state_machine->height_cut_length);
                            cut_state_machine->left_head_pos_value = *(cut_state_machine->cut_left_angle);
                            cut_state_machine->right_head_pos_value = *(cut_state_machine->cut_right_angle);
                        
                            if (cut_state_machine->bottom_cut_length_value < cut_state_machine->min_limit)
                            {
                                cut_state_machine->current_cut_type = SHORT_CUT;
                            }
                            else if (cut_state_machine->bottom_cut_length_value >= cut_state_machine->min_limit && cut_state_machine->bottom_cut_length_value <= cut_state_machine->max_limit)
                            {
                                cut_state_machine->current_cut_type = NORMAL_CUT;
                            }
                            else
                            {
                                cut_state_machine->current_cut_type = LONG_CUT;
                            }

                            cut_state_machine->state = POSITIONING_HEAD_ANGLES;
                        }
                    }
                }                     

                break;   

            case POSITIONING_HEAD_ANGLES:
                if (cut_state_machine->angle_head_type_actuator == PNEUMATIC_ACTUATOR)
                {
                    if (cut_state_machine->left_head_pos_value <= 90)
                    {
                        *(cut_state_machine->left_head) = 1;
                    }
                    else
                    {
                        *(cut_state_machine->left_head) = 0;
                    }

                    if (cut_state_machine->right_head_pos_value <= 90)
                    {
                        *(cut_state_machine->right_head) = 1;
                    }
                    else
                    {
                        *(cut_state_machine->right_head) = 0;
                    }
                }

                cut_state_machine->busy_hand_btns_state = false;
                *(cut_state_machine->status) = PRESS_HANDS_BUSY_BUTTONS_FOR_MOVE;
                cut_state_machine->state = WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_START_MOVE;
                break;          
                
            case WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_START_MOVE:
                if (cut_state_machine->busy_hand_btns_state)
                {
                    cut_state_machine->busy_hand_btns_state = false;
                    cut_state_machine->state = SELECT_CUT_TYPE;
                }
                break;

            case SELECT_CUT_TYPE:

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

                break;

            case NORMAL_CUT:

                if ((fabs(*(cut_state_machine->pos_fb) - cut_state_machine->bottom_cut_length_value) > cut_state_machine->ferror) && !*(cut_state_machine->start_move))
                {
                    *(cut_state_machine->move_to_length) = cut_state_machine->bottom_cut_length_value;
                    // *(cut_state_machine->start_move) = 1; 
                    // cut_state_machine->state = WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL;
                    cut_state_machine->state = DEACTIVATE_BREAK;
                }

                if (!*(cut_state_machine->start_move))
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_MSG)
                    {
                       cut_state_machine->delay_count = 0; 
                       cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                    }
                }   

                break;

            case DEACTIVATE_BREAK:
                cut_state_machine->break_nedded = true;
                // cut_state_machine->delay_count++;
                // if (cut_state_machine->delay_count == COUNT_BREAK)
                // {
                //     cut_state_machine->delay_count = 0;
                    *(cut_state_machine->start_move) = 1; 
                    cut_state_machine->state = WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL;
                // }
                break;

            case WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL:
                if (!*(cut_state_machine->start_move))
                {
                    *(cut_state_machine->start_move) = 0;
                    cut_state_machine->state = WAITING_FOR_LOW_LEVEL_IN_POS_SIGNAL;
                }
                break;

            case WAITING_FOR_LOW_LEVEL_IN_POS_SIGNAL:
                if (!(*(cut_state_machine->in_pos)))
                {
                    cut_state_machine->state = WAITING_FOR_MACHINE_IN_POSITION;
                }
                break;

            case WAITING_FOR_MACHINE_IN_POSITION:
                if (*(cut_state_machine->in_pos))
                {
                    // cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;

                    cut_state_machine->state = ACTIVATE_BREAK;
                }
                break;

            case ACTIVATE_BREAK:
                if (!((cut_state_machine->current_cut_type == LONG_CUT) && step_long_cut == 1))
                {
                    // cut_state_machine->delay_count++;
                    // if (cut_state_machine->delay_count == COUNT_BREAK)
                    // {
                    //     cut_state_machine->delay_count = 0;
                        cut_state_machine->break_nedded = false;
                        cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                    // }
                }
                else
                {
                    cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                }
                break;

            case WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED:

                if (cut_state_machine->clamps_button_state)
                {                        
                    cut_state_machine->clamps_button_state = false;
                    cut_state_machine->busy_hand_btns_state = false;

                    if (cut_state_machine->current_cut_type == SHORT_CUT)
                    {
                        *(cut_state_machine->right_clamp) = 1;
                        *(cut_state_machine->left_clamp) = 0;
                    }
                    else if (cut_state_machine->current_cut_type == NORMAL_CUT)
                    {
                        *(cut_state_machine->right_clamp) = 1;
                        *(cut_state_machine->left_clamp) = 1;
                    }
                    else if (cut_state_machine->current_cut_type == LONG_CUT)
                    {
                        if (step_long_cut == 0)
                        {
                            *(cut_state_machine->right_clamp) = 1;
                            *(cut_state_machine->left_clamp) = 1;
                        }
                    }

                    *(cut_state_machine->status) = PRESS_BUSY_HANDS_BUTTONS_FOR_CUT;
                    cut_state_machine->state = WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_CUT;
                }
                else
                {
                    if (cut_state_machine->current_cut_type == LONG_CUT && !(step_long_cut == 0))
                    {

                        *(cut_state_machine->right_clamp) = 1;
                        *(cut_state_machine->left_clamp) = 1;
                        cut_state_machine->state = CHANGE_STATE_CLAMPS_LONG_CUT_FOR_STEP_1_2;
                    }
                    else
                    {
                        *(cut_state_machine->status) = CLOSE_CLAMPS;
                        *(cut_state_machine->right_clamp) = 0;
                        *(cut_state_machine->left_clamp) = 0;
                    }
                }

                break;

            case CHANGE_STATE_CLAMPS_LONG_CUT_FOR_STEP_1_2:
                cut_state_machine->delay_count++;
                if (cut_state_machine->delay_count == COUNT_CLAMP_OPEN_LONG_CUT)
                {
                    cut_state_machine->delay_count = 0;
                    if (step_long_cut == 1)
                    {
                        *(cut_state_machine->right_clamp) = 0;
                        *(cut_state_machine->left_clamp) = 1;

                    }
                    else if (step_long_cut == 2)
                    {
                        *(cut_state_machine->right_clamp) = 1;
                        *(cut_state_machine->left_clamp) = 1;
                        *(cut_state_machine->status) = PRESS_BUSY_HANDS_BUTTONS_FOR_CUT;

                    }
                    cut_state_machine->state = WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_CUT;
                }
                break;

            case WAITING_FOR_BUSY_HANDS_BUTTONS_TO_BE_PRESSED_TO_CUT:

                if (!(cut_state_machine->init_left_cut) && !(cut_state_machine->init_right_cut))
                {
                    if (cut_state_machine->busy_hand_btns_state)
                    {
                        cut_state_machine->busy_hand_btns_state = false;

                        if (cut_state_machine->current_cut_type == NORMAL_CUT)
                        {

                            if (!(*(cut_state_machine->left_saw_blade)) && (*(cut_state_machine->right_saw_blade)))
                            {
                                *(cut_state_machine->status) = CUT_ONLY_RIGHT_SAW_BLADE;
                                cut_state_machine->init_right_cut = true;
                                cut_state_machine->init_left_cut = false;
                                wait_for_msg = true;
                            } 
                            else if ((*(cut_state_machine->left_saw_blade)) && !(*(cut_state_machine->right_saw_blade)))
                            {
                                *(cut_state_machine->status) = CUT_ONLY_LEFT_SAW_BLADE;
                                cut_state_machine->init_left_cut = true;
                                cut_state_machine->init_right_cut = false;
                                wait_for_msg = true;
                            }
                            else if (!(*(cut_state_machine->left_saw_blade)) && !(*(cut_state_machine->right_saw_blade)))
                            {
                                *(cut_state_machine->status) = TURN_ON_SAW_BLADES_AND_PRESS_HANDS_BUSY_BUTTONS;
                                cut_state_machine->init_left_cut = false;
                                cut_state_machine->init_right_cut = false;
                            }
                            else
                            {
                                *(cut_state_machine->status) = CUT_BOTH_SAW_BLADES;
                                cut_state_machine->init_right_cut = true;
                                cut_state_machine->init_left_cut = true;   
                                wait_for_msg = true;                         
                            }
                        }
                        else if (cut_state_machine->current_cut_type == SHORT_CUT)
                        {
                            if (!(*(cut_state_machine->right_saw_blade)))
                            {
                                *(cut_state_machine->status) = TURN_ON_RIGHT_SAW_BLADE_AND_PRESS_HANDS_BUSY_BUTTONS;
                            }
                            else
                            {
                                *(cut_state_machine->status) = CUT_ONLY_RIGHT_SAW_BLADE_SHORT_CUT;
                                cut_state_machine->init_left_cut = false;
                                cut_state_machine->init_right_cut = true;
                                wait_for_msg = true;
                            }
                        }
                        else if (cut_state_machine->current_cut_type == LONG_CUT)
                        {
                            if (step_long_cut == 0)
                            {
                                if (!(*(cut_state_machine->left_saw_blade)))
                                {
                                    *(cut_state_machine->status) = TURN_ON_LEFT_SAW_BLADE_AND_PRESS_HANDS_BUSY_BUTTONS;
                                }
                                else
                                {
                                    *(cut_state_machine->status) = CUT_ONLY_LEFT_SAW_BLADE;
                                    cut_state_machine->init_left_cut = true;
                                    cut_state_machine->init_right_cut = false;
                                    wait_for_msg = true;
                                }
                            }
                            else if (step_long_cut == 1)
                            {
                                cut_state_machine->init_left_cut = false;
                                cut_state_machine->init_right_cut = false;
                                wait_for_msg = true;
                                skip_cut = true;
                            }
                            else if (step_long_cut == 2)
                            {
                                if (!(*(cut_state_machine->right_saw_blade)))
                                {
                                    *(cut_state_machine->status) = TURN_ON_RIGHT_SAW_BLADE_AND_PRESS_HANDS_BUSY_BUTTONS;
                                }
                                else
                                {

                                    *(cut_state_machine->status) = CUT_ONLY_RIGHT_SAW_BLADE;
                                    cut_state_machine->init_left_cut = false;
                                    cut_state_machine->init_right_cut = true;
                                    wait_for_msg = true;
                                }
                            }
                            
                        }

                    }
                }

                if (cut_state_machine->clamps_button_state)
                {
                    cut_state_machine->clamps_button_state = false;
                    *(cut_state_machine->left_clamp) = 0;
                    *(cut_state_machine->right_clamp) = 0;
                    cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                }
                else if (wait_for_msg)
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_MSG)
                    {
                        cut_state_machine->delay_count = 0;
                        wait_for_msg = false;
                    }
                }
                else if (skip_cut)
                {
                    cut_state_machine->state = CUT_COMPLETE_SEND_PULSE;
                    skip_cut = false;
                }
                else if (cut_state_machine->init_left_cut || cut_state_machine->init_right_cut)
                {
                    cut_state_machine->end_cut = false;
                    if (*(cut_state_machine->saw_blade_output_time) > 0)
                    {
                        *(cut_state_machine->status) = CUT_CONTROLLED_BY_TIME;
                        cut_state_machine->delay_count++;
                        if (cut_state_machine->delay_count == COUNT_MSG)
                        {
                            cut_state_machine->delay_count = 0;
                            cut_state_machine->state = SAW_BLADE_OUTPUT_CONTROLLED_BY_TIME;
                        }
                    }
                    else
                    {
                        *(cut_state_machine->status) = CUT_CONTROLLED_BY_USER;
                        cut_state_machine->delay_count++;
                        if (cut_state_machine->delay_count == COUNT_MSG)
                        {
                            cut_state_machine->delay_count = 0;
                            cut_state_machine->state = SAW_BLADE_OUTPUT_CONTROLLED_BY_USER;
                        }
                    }
                }

                break;


            case SAW_BLADE_OUTPUT_CONTROLLED_BY_TIME:

                if (cut_state_machine->init_left_cut)
                {
                    *(cut_state_machine->left_saw_blade_output_move) = 1;
                    cut_state_machine->delay_count_left_saw_blade++;
                    if (cut_state_machine->delay_count_left_saw_blade == *(cut_state_machine->saw_blade_output_time))
                    {
                        cut_state_machine->delay_count_left_saw_blade = 0;
                        *(cut_state_machine->left_saw_blade_output_move) = 0;
                        cut_state_machine->init_left_cut = false;
                        cut_state_machine->end_cut = true;
                    }
                }

                if (cut_state_machine->init_right_cut)
                {
                    *(cut_state_machine->right_saw_blade_output_move) = 1;
                    cut_state_machine->delay_count_right_saw_blade++;
                    if (cut_state_machine->delay_count_right_saw_blade == *(cut_state_machine->saw_blade_output_time))
                    {
                        cut_state_machine->delay_count_right_saw_blade = 0;
                        *(cut_state_machine->right_saw_blade_output_move) = 0;
                        cut_state_machine->init_right_cut = false;
                        cut_state_machine->end_cut = true;
                    }
                }

                if (cut_state_machine->end_cut)
                {
                    cut_state_machine->end_cut = false;
                    cut_state_machine->state = DELAY_OPEN_CLAMPS;
                }

                break;

            case SAW_BLADE_OUTPUT_CONTROLLED_BY_USER:

                if (cut_state_machine->init_left_cut)
                {
                    if (cut_state_machine->busy_hand_btns_state)
                        *(cut_state_machine->left_saw_blade_output_move) = 1;
                    
                    if (cut_state_machine->falling_edge_detector_busy_hand_btns.out)
                    {
                        cut_state_machine->busy_hand_btns_state = false;
                        *(cut_state_machine->left_saw_blade_output_move) = 0;
                        cut_state_machine->init_left_cut = false;
                        cut_state_machine->end_cut = true;
                    }
                }

                if (cut_state_machine->init_right_cut)
                {
                    if (cut_state_machine->busy_hand_btns_state)
                        *(cut_state_machine->right_saw_blade_output_move) = 1;
                    
                    if (cut_state_machine->falling_edge_detector_busy_hand_btns.out)
                    {
                        cut_state_machine->busy_hand_btns_state = false;
                        *(cut_state_machine->right_saw_blade_output_move) = 0;
                        cut_state_machine->init_right_cut = false;
                        cut_state_machine->end_cut = true;
                    }
                }

                if (cut_state_machine->end_cut)
                {
                    cut_state_machine->end_cut = false;
                    cut_state_machine->state = DELAY_OPEN_CLAMPS;
                }

                break;

            case DELAY_OPEN_CLAMPS:
                if (!(cut_state_machine->current_cut_type == LONG_CUT && (step_long_cut == 0 || step_long_cut == 1)))
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_CLAMP_OPEN)
                    {
                        cut_state_machine->delay_count = 0;
                        *(cut_state_machine->right_clamp) = 0;
                        *(cut_state_machine->left_clamp) = 0;
                        cut_state_machine->state = SEND_CUT_COMPLETE_MSG;
                    }
                }
                else
                {
                    cut_state_machine->state = CUT_COMPLETE_SEND_PULSE;
                }
                break;

            case SEND_CUT_COMPLETE_MSG:
                *(cut_state_machine->status) = CUT_COMPLETE;
                cut_state_machine->delay_count++;
                if (cut_state_machine->delay_count == COUNT_MSG)
                {
                    cut_state_machine->delay_count = 0;
                    cut_state_machine->state = CUT_COMPLETE_SEND_PULSE;
                }
                break;

            case CUT_COMPLETE_SEND_PULSE:
                if (cut_state_machine->current_cut_type == LONG_CUT)
                {
                    step_long_cut++;
                    if (step_long_cut == 3)
                    {
                        step_long_cut = 0;
                        *(cut_state_machine->cut_complete) = 1;
                        if (cut_state_machine->number_of_cuts_value > 1)
                        {
                            cut_state_machine->state = SELECT_CUT_TYPE;
                        }
                        else
                        {
                            cut_state_machine->state = IDLE;
                        }
                        cut_state_machine->number_of_cuts_value--;
                        *(cut_state_machine->number_of_cuts) = cut_state_machine->number_of_cuts_value;
                    }
                    else
                    {
                        *(cut_state_machine->cut_complete) = 0;
                        cut_state_machine->state = LONG_CUT;
                    }
                }
                else
                {
                    *(cut_state_machine->cut_complete) = 1;
                    if (cut_state_machine->number_of_cuts_value > 1)
                    {
                        cut_state_machine->state = SELECT_CUT_TYPE;
                    }
                    else
                    {
                        cut_state_machine->state = IDLE;
                    }
                    cut_state_machine->number_of_cuts_value--;
                    *(cut_state_machine->number_of_cuts) = cut_state_machine->number_of_cuts_value;
                }
                break;

            
            case SHORT_CUT:

                float short_cut_length;

                if (cut_state_machine->bottom_cut_length_value < cut_state_machine->top_cut_length_value)
                {
                    short_cut_length = cut_state_machine->bottom_cut_length_value + tan(cut_state_machine->left_head_pos_value * M_PI / 180.0) * cut_state_machine->height_cut_value;
                }
                else
                {
                    short_cut_length = cut_state_machine->bottom_cut_length_value;
                }

                if (fabs(*(cut_state_machine->pos_fb) - short_cut_length - cut_state_machine->min_cut_top_position) > cut_state_machine->ferror)
                {
                    *(cut_state_machine->move_to_length) = short_cut_length + cut_state_machine->min_cut_top_position;
                    // *(cut_state_machine->start_move) = 1; 
                    // cut_state_machine->state = WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL;
                    cut_state_machine->state = DEACTIVATE_BREAK;
                }

                if (!*(cut_state_machine->start_move))
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_MSG)
                    {
                       cut_state_machine->delay_count = 0; 
                       cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                    }
                }
                break;


            case LONG_CUT:

                if (step_long_cut == 0 || step_long_cut == 2)
                {
                    if (fabs(*(cut_state_machine->pos_fb) - cut_state_machine->max_limit) > cut_state_machine->ferror)
                    {
                        *(cut_state_machine->move_to_length) = cut_state_machine->max_limit;
                        // *(cut_state_machine->start_move) = 1; 
                        // cut_state_machine->state = WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL;
                        cut_state_machine->state = DEACTIVATE_BREAK;
                    }
                }
                else if (step_long_cut == 1)
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_CLAMP_OPEN)
                    {
                        cut_state_machine->delay_count = 0;
                        *(cut_state_machine->left_clamp) = 0;
                        *(cut_state_machine->right_clamp) = 1;
                    }
                    else
                    {
                        break;
                    }
                    if (fabs(*(cut_state_machine->pos_fb) - fabs(cut_state_machine->max_limit - cut_state_machine->bottom_cut_length_value)) > cut_state_machine->ferror)
                    {
                        *(cut_state_machine->move_to_length) = cut_state_machine->max_limit - fabs(cut_state_machine->max_limit - cut_state_machine->bottom_cut_length_value);
                        // *(cut_state_machine->start_move) = 1; 
                        // cut_state_machine->state = WAITING_FOR_LOW_LEVEL_START_MOVE_SIGNAL;
                        cut_state_machine->state = DEACTIVATE_BREAK;
                        *(cut_state_machine->status) = PRESS_BUSY_HAND_BTNS_FOR_MOVE_TO_RECOVER_LENGTH_LONG_CUT;
                    }

                }

                if (!*(cut_state_machine->start_move))
                {
                    cut_state_machine->delay_count++;
                    if (cut_state_machine->delay_count == COUNT_MSG)
                    {
                        cut_state_machine->delay_count = 0; 
                        cut_state_machine->state = WAITING_FOR_CLAMPS_BUTTON_TO_BE_PRESSED;
                    }
                }

                break;
        }   
    
        switch (cut_state_machine->break_state)
        {
            case WAITING_FOR_BREAK_TO_BE_DEACTIVATED:
                
                if ((cut_state_machine->break_nedded && *(cut_state_machine->busy_hand_btns)) || *(cut_state_machine->homing_start))
                {
                    
                    *(cut_state_machine->breaks) = 1;
                    *(cut_state_machine->homing_break_deactivate) = 0;
                    cut_state_machine->delay_count_break++;
                    if (cut_state_machine->delay_count_break == COUNT_BREAK)
                    {
                        cut_state_machine->delay_count_break = 0;
                        
                        if ( *(cut_state_machine->homing_start))
                        {
                            *(cut_state_machine->homing_break_deactivate) = 1;
                            cut_state_machine->break_state = WAITING_FOR_HOMING_START_LOW_LEVEL;
                        }
                        else
                        {
                            *(cut_state_machine->feed_inhibit) = 0;
                            cut_state_machine->break_state = WAITING_FOR_BREAK_TO_BE_ACTIVATED_WORK_MODE;
                        }
                    }
                }
                break;

            case WAITING_FOR_HOMING_START_LOW_LEVEL:
                if (!*(cut_state_machine->homing_start) && *(cut_state_machine->homing))
                {
                    cut_state_machine->break_state = WAITING_FOR_BREAK_TO_BE_ACTIVATED_HOMING_MODE;
                }
                break;

            case WAITING_FOR_BREAK_TO_BE_ACTIVATED_WORK_MODE:
                if (!(cut_state_machine->break_nedded && *(cut_state_machine->busy_hand_btns)))
                {
                    *(cut_state_machine->feed_inhibit) = 1;
                    cut_state_machine->break_state = BREAK_ACTIVATED;
                }
                break;

            case WAITING_FOR_BREAK_TO_BE_ACTIVATED_HOMING_MODE:
                if (!*(cut_state_machine->homing))
                {
                    *(cut_state_machine->homing_break_deactivate) = 0;
                    cut_state_machine->break_state = BREAK_ACTIVATED;
                }
                break;

            case BREAK_ACTIVATED:
                cut_state_machine->delay_count_break++;
                if (cut_state_machine->delay_count_break == COUNT_BREAK)
                {
                    cut_state_machine->delay_count_break = 0;
                    *(cut_state_machine->breaks) = 0;
                    cut_state_machine->break_state = WAITING_FOR_BREAK_TO_BE_DEACTIVATED;
                }
                break;

        }
    }
}

void edges_detection_update(void *arg, long period) {

    cut_state_machine_t *cut_state_machine = (cut_state_machine_t *)arg;

    if (!init_params_edge_detector) {

        cut_state_machine->rising_edge_detector_clamps_btn.both = (bool)cut_state_machine->edge_detector_clamps_btn_both;
        cut_state_machine->rising_edge_detector_clamps_btn.in_edge = (bool)cut_state_machine->edge_detector_clamps_btn_in_edge;
        cut_state_machine->rising_edge_detector_clamps_btn.out_width_pulses = cut_state_machine->edge_detector_clamps_btn_out_width_pulses;
        
        cut_state_machine->falling_edge_detector_clamps_btn.both = (bool)cut_state_machine->edge_detector_clamps_btn_both;
        cut_state_machine->falling_edge_detector_clamps_btn.in_edge = !(bool)cut_state_machine->edge_detector_clamps_btn_in_edge;
        cut_state_machine->falling_edge_detector_clamps_btn.out_width_pulses = cut_state_machine->edge_detector_clamps_btn_out_width_pulses;

        cut_state_machine->rising_edge_detector_busy_hand_btns.both = (bool)cut_state_machine->edge_detector_busy_hand_btns_both;
        cut_state_machine->rising_edge_detector_busy_hand_btns.in_edge = (bool)cut_state_machine->edge_detector_busy_hand_btns_in_edge;
        cut_state_machine->rising_edge_detector_busy_hand_btns.out_width_pulses = cut_state_machine->edge_detector_busy_hand_btns_out_width_pulses;

        cut_state_machine->falling_edge_detector_busy_hand_btns.both = (bool)cut_state_machine->edge_detector_busy_hand_btns_both;
        cut_state_machine->falling_edge_detector_busy_hand_btns.in_edge = !(bool)cut_state_machine->edge_detector_busy_hand_btns_in_edge;
        cut_state_machine->falling_edge_detector_busy_hand_btns.out_width_pulses = cut_state_machine->edge_detector_busy_hand_btns_out_width_pulses;

        init_params_edge_detector = true;
    }

    // Left Hand Button State Update

    if (edge_detector(&(cut_state_machine->rising_edge_detector_busy_hand_btns), *(cut_state_machine->busy_hand_btns)))
    {
        cut_state_machine->busy_hand_btns_state = true;
    }
    else if (edge_detector(&(cut_state_machine->falling_edge_detector_busy_hand_btns), *(cut_state_machine->busy_hand_btns)))
    {
        cut_state_machine->busy_hand_btns_state = false;
    }

    // Clamps button State Update

    if (edge_detector(&(cut_state_machine->rising_edge_detector_clamps_btn), *(cut_state_machine->clamps_button)))
    {
        cut_state_machine->clamps_button_state = true;
    }
    else if (edge_detector(&(cut_state_machine->falling_edge_detector_clamps_btn), *(cut_state_machine->clamps_button)))
    {
        cut_state_machine->clamps_button_state = false;
    }

}

uint8_t edge_detector(edge_detector_t *detector, uint8_t in_signal_value) {
    int new_in = in_signal_value;  
    if (detector->pulse_count > 0) {
        detector->pulse_count--;
    }
    if (!detector->first) {
        int rise = new_in && !detector->last_in;
        int fall = !new_in && detector->last_in;
        int desired_edge = detector->both ? rise || fall : detector->in_edge ? fall : rise;
        if (desired_edge) {
            detector->pulse_count = detector->out_width_pulses;
            detector->out = 1;
        } else if (detector->pulse_count > 0) {
            detector->out = 1;
        } else {
            detector->pulse_count = 0;
            detector->out = 0;
        }
    } else {
        detector->first = false;
    }
    detector->last_in = new_in;
    return detector->out;
}
