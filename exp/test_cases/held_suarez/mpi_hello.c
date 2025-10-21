#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
    int world_size, world_rank;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    MPI_Init(&argc, &argv);                          // Initialize MPI environment
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);      // Get total number of MPI processes
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);      // Get rank of this process
    MPI_Get_processor_name(processor_name, &name_len);// Get hostname

    printf("Hello from processor %s, rank %d out of %d processes\n", processor_name, world_rank, world_size);

    MPI_Finalize();                                  // Clean up MPI environment
    return 0;
}

