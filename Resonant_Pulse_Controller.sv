// Resonant_Pulse_Controller.sv
// License: CC-BY-NC 4.0
// Author: Jonathan Alan Reed

`timescale 1ns/1ps

module n2_mfc_core #(
    // 1768.94 fs expressed as an integer count of 10-attosecond steps
    parameter [31:0] TARGET_STEPS = 32'd176_894
)(
    input  logic         clk,       // 10-attosecond clock
    input  logic         rst_n,     
    input  logic         trigger,   
    output logic [63:0]  out_freq,  
    output logic         snap_done  
);

    localparam [63:0] START_FREQ = 64'd70_700_000_000_000; 
    // Chirp: -4.73e24 Hz/s. In 10as, that's exactly 47,300 Hz.
    localparam [63:0] CHIRP_STEP = 64'd47_300; 

    logic [63:0] freq_reg;
    logic [31:0] step_counter;
    
    enum {IDLE, CHIRP, DONE} state;

    assign out_freq = (state == CHIRP) ? freq_reg : 64'd0;
    assign snap_done = (state == DONE);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            freq_reg     <= START_FREQ;
            step_counter <= 0;
        end else begin
            case (state)
                IDLE: begin
                    if (trigger) state <= CHIRP;
                    freq_reg     <= START_FREQ;
                    step_counter <= 0;
                end
                CHIRP: begin
                    freq_reg     <= freq_reg - CHIRP_STEP;
                    step_counter <= step_counter + 1;
                    // Trigger exactly at step 176,894
                    if (step_counter >= TARGET_STEPS - 1) state <= DONE;
                end
                DONE: if (!trigger) state <= IDLE;
            endcase
        end
    end
endmodule