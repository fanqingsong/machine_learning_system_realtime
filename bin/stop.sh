
for job in `jps -q`; do
    kill -9 ${job}
done

