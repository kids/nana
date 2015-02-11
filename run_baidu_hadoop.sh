#!/bin/sh 
workpath=/home/work/rewrite/src/radoop app=url2list home="/app/st/nlp/zry" input="/log/20120604/0000/rank-hdfs.dmop/part-*" 
output="$home/out01/ 
pkgpath="$home/$app.tar.gz" 

cd $workpath/$app 
tar czvf ../$app.tar.gz * 
cd $workpath 

hadoop fs -test -e $pkgpath && hadoop fs -rm $pkgpath 
hadoop fs -put $app.tar.gz $pkgpath 
hadoop fs -test -d $output && hadoop fs -rmr $output 

hadoop streaming \
 -D stream.num.map.output.key.fields=3 \
 -D mapred.text.key.partitioner.options="-k1,2" \
 -D mapred.text.key.comparator.options="-k3" \
 -D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \ 
-mapper "python26/bin/python26.sh url2list/url_pairs.py" \
 -reducer "sh url2list/reducer.sh" \
 -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner \
 -input $input \ -output $output \
 -cacheArchive "/share/python26.tar.gz#python26" \
 -cacheArchive "$pkgpath#url2list" \
 -jobconf mapred.job.name="score_zry_$app" \
 -jobconf mapred.job.priority=HIGH \
 -jobconf mapred.job.map.capacity=600 \
 -jobconf mapred.job.reduce.capacity=60 \
 -jobconf mapred.map.tasks=600 \
 -jobconf mapred.reduce.tasks=60


#reducer.sh

#!/bin/sh                  
app=pair2index
home="/ps/ubs/score/zry"
export LD_LIBRARY_PATH="$app/sphinx/tokyo"
python26/bin/python26.sh $app/sphinx/setconf.py
#echo $mapred_work_output_dir >&2 
#echo $PWD >&2                                                                                  
#ls >&2                
#cat sphinx.conf >&2                                                                              
$app/sphinx/indexer --config $PWD/sphinx.conf --all >&2
$HADOOP_HOME/bin/hadoop fs -D hadoop.job.ugi=$hadoop_job_ugi -put $PWD/bdb* $mapred_work_output_dir
$HADOOP_HOME/bin/hadoop fs -D hadoop.job.ugi=$hadoop_job_ugi -put $PWD/idx*
$mapred_work_output_dir