#!/bin/bash
# Create logs and sequences directories if they don't exist
mkdir -p logs sequences_recursive

# Check if no arguments are provided, then use all defaults
if [ "$#" -eq 0 ]; then
    echo "No arguments provided. Using default values."
    K=3
    PRIOR_1="GGC"
    PRIOR_2="arm"
    PRIOR_3="NMA"
    PRIOR_4="GAA"
    PRIOR_5="inc"
    S=500 # Default sequence length
    T=10
    ALPHA=0.1
else
    # Initialize variables to track what was provided
    K_PROVIDED=0
    PRIOR1_PROVIDED=0
    PRIOR2_PROVIDED=0
    PRIOR3_PROVIDED=0
    PRIOR4_PROVIDED=0
    PRIOR5_PROVIDED=0
    S_PROVIDED=0
    T_PROVIDED=0
    ALPHA_PROVIDED=0

    # Parse named arguments and track what was provided
    while [ "$#" -gt 0 ]; do
        case "$1" in
            -k|--k)
                K="$2"
                K_PROVIDED=1
                shift 2
                ;;
            -p1|--prior1)
                PRIOR_1="$2"
                PRIOR1_PROVIDED=1
                shift 2
                ;;
            -p2|--prior2)
                PRIOR_2="$2"
                PRIOR2_PROVIDED=1
                shift 2
                ;;
            -p3|--prior3)
                PRIOR_3="$2"
                PRIOR3_PROVIDED=1
                shift 2
                ;;
            -p4|--prior4)
                PRIOR_4="$2"
                PRIOR4_PROVIDED=1
                shift 2
                ;;
            -p5|--prior5)
                PRIOR_5="$2"
                PRIOR5_PROVIDED=1
                shift 2
                ;;
            -s|--sequence-length)
                S="$2"
                S_PROVIDED=1
                shift 2
                ;;
            -t|--iterations)
                T="$2"
                T_PROVIDED=1
                shift 2
                ;;
            -a|--alpha)
                ALPHA="$2"
                ALPHA_PROVIDED=1
                shift 2
                ;;
            *)
                echo "Unknown parameter: $1"
                echo "Usage: $0 [-k <value>] [-p1 <prior1>] [-p2 <prior2>] [-p3 <prior3>] [-p4 <prior4>] [-p5 <prior5>] [-s <sequence_length>] [-t <iterations>] [-a <alpha>]"
                exit 1
                ;;
        esac
    done

    # Check if K is provided but not all priors, or if any prior is provided but not K
    if [ $K_PROVIDED -eq 1 ] && ([ $PRIOR1_PROVIDED -eq 0 ] || [ $PRIOR2_PROVIDED -eq 0 ] || [ $PRIOR3_PROVIDED -eq 0 ] || [ $PRIOR4_PROVIDED -eq 0 ] || [ $PRIOR5_PROVIDED -eq 0 ]); then
        echo "Error: If K is provided, all five priors must also be provided."
        echo "Usage: $0 [-k <value>] [-p1 <prior1>] [-p2 <prior2>] [-p3 <prior3>] [-p4 <prior4>] [-p5 <prior5>] [-s <sequence_length>] [-t <iterations>] [-a <alpha>]"
        exit 1
    fi

    if [ $K_PROVIDED -eq 0 ] && ([ $PRIOR1_PROVIDED -eq 1 ] || [ $PRIOR2_PROVIDED -eq 1 ] || [ $PRIOR3_PROVIDED -eq 1 ] || [ $PRIOR4_PROVIDED -eq 1 ] || [ $PRIOR5_PROVIDED -eq 1 ]); then
        echo "Error: If any prior is provided, K must also be provided."
        echo "Usage: $0 [-k <value>] [-p1 <prior1>] [-p2 <prior2>] [-p3 <prior3>] [-p4 <prior4>] [-p5 <prior5>] [-s <sequence_length>] [-t <iterations>] [-a <alpha>]"
        exit 1
    fi

    # Set values based on what was provided
    if [ $K_PROVIDED -eq 0 ]; then
        # Neither K nor priors were provided, use defaults
        K=3
        PRIOR_1="GGC"
        PRIOR_2="arm"
        PRIOR_3="NMA"
        PRIOR_4="GAA"
        PRIOR_5="inc"
    fi

    # Set defaults for other parameters if not provided
    if [ $S_PROVIDED -eq 0 ]; then
        S=500
    fi
    
    if [ $T_PROVIDED -eq 0 ]; then
        T=10
    fi
    
    if [ $ALPHA_PROVIDED -eq 0 ]; then
        ALPHA=0.1
    fi
fi

# Display settings being used
echo "Running with the following settings:"
echo "K = $K"
echo "PRIOR_1 = $PRIOR_1"
echo "PRIOR_2 = $PRIOR_2"
echo "PRIOR_3 = $PRIOR_3"
echo "PRIOR_4 = $PRIOR_4"
echo "PRIOR_5 = $PRIOR_5"
echo "S (Sequence Length) = $S"
echo "T (Iterations) = $T"
echo "ALPHA = $ALPHA"

# Store priors in an array
PRIOR_LIST=("$PRIOR_1" "$PRIOR_2" "$PRIOR_3" "$PRIOR_4" "$PRIOR_5")

# Define sequence files
SEQUENCE_FILES=("sequence1.txt" "sequence2.txt" "sequence3.txt" "sequence4.txt" "sequence5.txt")

# Create CSV file to store AIC and Entropy values
echo "Iteration,File,k,Alpha,Prior,Sequence_Length,AIC,Entropy" > aic_results_recursive.csv

# Loop through all sequence files
for i in "${!SEQUENCE_FILES[@]}"
do
    INPUT_FILE="sequences/${SEQUENCE_FILES[$i]}"
    PRIOR=${PRIOR_LIST[$i]}
    FILE_NAME=$(basename "$INPUT_FILE" .txt)
    
    for ((iter=1; iter<=T; iter++))
    do
        echo "Processing: $FILE_NAME - Iteration $iter - Prior: $PRIOR - Sequence Length: $S"
        
        # Run FCM and save log
        ./fcm "$INPUT_FILE" -k $K -a $ALPHA > "logs/${FILE_NAME}_iteration_${iter}_fcm.log"
        
        # Extract AIC and Entropy from log
        ENTROPY=$(grep "Entropy:" "logs/${FILE_NAME}_iteration_${iter}_fcm.log" | awk '{print $2}')
        AIC=$(grep "Average Information Content:" "logs/${FILE_NAME}_iteration_${iter}_fcm.log" | awk '{print $4}')
        
        if [ -z "$AIC" ] || [ -z "$ENTROPY" ]; then
            echo "Error: Failed to extract AIC or Entropy from logs/${FILE_NAME}_iteration_${iter}_fcm.log!"
            exit 1
        fi
        
        # Save results in CSV file
        echo "$iter,$FILE_NAME,$K,$ALPHA,$PRIOR,$S,$AIC,$ENTROPY" >> aic_results_recursive.csv
        
        # Run generator with the correct prior and sequence length (-s) and save log
        ./generator model.txt -p "$PRIOR" -s "$S" > "logs/${FILE_NAME}_iteration_${iter}_gen.log"
        
        # Rename generated output for next iteration
        mv generated_output.txt "sequences_recursive/${FILE_NAME}_sequence_${iter}.txt"
        
        # Use new sequence for next iteration
        INPUT_FILE="sequences_recursive/${FILE_NAME}_sequence_${iter}.txt"
    done
done

echo "Recursive process completed!"